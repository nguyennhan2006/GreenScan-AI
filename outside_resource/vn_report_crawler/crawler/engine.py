"""Engine điều phối: adapter phát hiện tài liệu, shared pipeline xử lý phần còn lại."""

from __future__ import annotations

import logging
from collections import deque
from datetime import UTC, datetime
from pathlib import Path

import httpx

from .adapters import CrawlContext, get_adapter
from .discovery.browser_fallback import diagnose_empty_listing
from .discovery.download_resolver import resolve_attachment_url
from .models import Candidate, CrawlStatus, SourceConfig
from .pipeline.deduplicator import Deduplicator
from .pipeline.downloader import Downloader, status_of
from .pipeline.manifest import ManifestWriter
from .pipeline.validator import detect_file_type
from .policies.rate_limit import RateLimiter
from .policies.robots import RobotsGate, SourceSkipped
from .storage.database import Database
from .storage.object_store import ObjectStore, make_document_id
from .utils import canonical_url, domain_allowed, filename_from_url

log = logging.getLogger(__name__)

_STATUS_TO_CRAWL_STATUS = {
    401: CrawlStatus.FORBIDDEN,
    403: CrawlStatus.FORBIDDEN,
    404: CrawlStatus.NOT_FOUND,
    410: CrawlStatus.NOT_FOUND,
}


class CrawlEngine:
    def __init__(
        self,
        config: SourceConfig,
        data_dir: Path,
        manifest: ManifestWriter,
        *,
        dry_run: bool = False,
        transport: httpx.BaseTransport | None = None,
    ):
        self.cfg = config
        self.data_dir = Path(data_dir)
        self.manifest = manifest
        self.dry_run = dry_run

        self.client = httpx.Client(
            headers={
                "User-Agent": config.user_agent,
                "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=httpx.Timeout(30.0, connect=15.0),
            verify=config.verify_ssl,
            transport=transport,
        )
        self.limiter = RateLimiter(config.delay_seconds, config.max_requests_per_minute)
        self.robots = RobotsGate(self.client, config.user_agent, config.robots_policy)
        self.downloader = Downloader(self.client, self.limiter)

        self.db = Database(self.data_dir)
        self.store = ObjectStore(self.data_dir)
        self.dedup = Deduplicator(self.store, self.db)

        ctx = CrawlContext(
            downloader=self.downloader, robots=self.robots, client=self.client, log=log
        )
        self.adapter = get_adapter(config.adapter)(config, ctx)

        self.visited: set[str] = set()
        self.documents_stored = 0
        self.js_rendered_pages: list[str] = []

    def close(self) -> None:
        self.client.close()
        self.db.close()

    # ---------------- helpers ----------------

    def _log_manifest(self, status: CrawlStatus, url: str, **extra) -> None:
        self.manifest.write(
            {
                "source_id": self.cfg.id,
                "adapter": self.cfg.adapter,
                "authority": self.cfg.authority.value,
                "url": url,
                "crawl_status": status.value,
                **extra,
            }
        )

    def _allowed(self, url: str) -> tuple[bool, str]:
        """Kiểm tra domain + robots. Ném SourceSkipped nếu policy yêu cầu dừng nguồn."""
        if not domain_allowed(url, self.cfg.allowed_domains):
            return False, "domain_not_allowed"
        return self.robots.can_fetch(url)

    # ---------------- xử lý attachment ----------------

    def handle_candidate(self, candidate: Candidate) -> None:
        if self.cfg.max_documents and self.documents_stored >= self.cfg.max_documents:
            return

        url = canonical_url(self.adapter.resolve_attachment(candidate))
        candidate = candidate.model_copy(update={"url": url})

        if self.db.should_skip(url):
            log.debug("Đã tải trước đó, bỏ qua: %s", url)
            return

        document_id = make_document_id(
            self.cfg.id, candidate.ticker or self.cfg.ticker,
            candidate.year, candidate.report_type, url,
        )
        discovery = {
            "source_id": self.cfg.id,
            "adapter": self.cfg.adapter,
            "source_authority": self.cfg.authority.value,
            "company": self.cfg.company,
            "ticker": candidate.ticker or self.cfg.ticker,
            "report_type": candidate.report_type,
            "title": candidate.title,
            "year": candidate.year,
            "source_page_url": candidate.source_page_url,
            "file_url": url,
            "canonical_source_url": candidate.canonical_source_url,
            "discovered_at": datetime.now(UTC).isoformat(),
            "metadata": candidate.hints,
        }
        self.db.upsert_discovery(document_id, discovery)

        if self.dry_run:
            log.info("[DRY RUN] %s | %s | %s", candidate.report_type, candidate.year, url)
            self._log_manifest(
                CrawlStatus.DISCOVERED, url,
                document_id=document_id, title=candidate.title,
                report_type=candidate.report_type, year=candidate.year,
            )
            return

        allowed, reason = self._allowed(url)
        if not allowed:
            self.db.mark_status(url, CrawlStatus.ROBOTS_DENIED, error_code=reason)
            self._log_manifest(CrawlStatus.ROBOTS_DENIED, url, document_id=document_id,
                               reason=reason)
            return

        try:
            response = self.downloader.get(url)
        except Exception as exc:  # noqa: BLE001
            code = status_of(exc)
            status = _STATUS_TO_CRAWL_STATUS.get(code or 0, CrawlStatus.TEMPORARY_ERROR)
            # Một dòng log ngắn, không phải full traceback cho mỗi URL hỏng.
            log.warning("Không tải được %s: %s", url, type(exc).__name__)
            log.debug("Chi tiết lỗi %s", url, exc_info=exc)
            self.db.mark_status(
                url,
                status,
                error_code=str(code or type(exc).__name__),
                error_message=str(exc)[:500],
            )
            self._log_manifest(status, url, document_id=document_id, error=str(exc)[:300])
            return

        # Trang xem trước nhúng file thật -> lấy URL bên trong rồi tải lại.
        embedded = resolve_attachment_url(response)
        if embedded:
            embedded = canonical_url(embedded)
            if embedded != url and domain_allowed(embedded, self.cfg.allowed_domains):
                self.handle_candidate(candidate.model_copy(update={"url": embedded}))
                return

        file_ext = detect_file_type(response)
        if file_ext is None:
            self.db.mark_status(url, CrawlStatus.INVALID_DOCUMENT,
                                error_code="unrecognized_content")
            self._log_manifest(CrawlStatus.INVALID_DOCUMENT, url, document_id=document_id)
            return

        if file_ext.lstrip(".") not in self.cfg.allowed_file_types:
            self.db.mark_status(url, CrawlStatus.UNSUPPORTED_TYPE, error_code=file_ext)
            self._log_manifest(CrawlStatus.UNSUPPORTED_TYPE, url, document_id=document_id,
                               file_format=file_ext.lstrip("."))
            return

        result = self.dedup.store_content(response.content, file_ext)
        meta = self.adapter.normalize_metadata(candidate, response, file_ext)
        meta["object_sha256"] = result.sha256
        meta["original_filename"] = filename_from_url(url)
        meta["object_path"] = str(result.path)

        self.db.mark_downloaded(
            url, result.sha256, file_ext.lstrip("."), meta["original_filename"],
            duplicate=result.is_duplicate,
        )
        # Canonical là thuộc tính của cả nhóm cùng object -> tính lại cho toàn nhóm
        # trong DB. KHÔNG đóng băng vào JSON của từng document, vì giá trị đó sẽ
        # lỗi thời ngay khi có bản mirror mới xuất hiện.
        canonical = self.dedup.refresh_canonical(result.sha256)
        self.store.put_document(document_id, meta)
        self.documents_stored += 1

        status = CrawlStatus.DUPLICATE if result.is_duplicate else CrawlStatus.DOWNLOADED
        log.info("%s %s -> %s", status.value, url, result.path.name)
        self._log_manifest(
            status, url,
            document_id=document_id,
            object_sha256=result.sha256,
            file_format=file_ext.lstrip("."),
            report_type=meta.get("report_type"),
            year=meta.get("year"),
            ticker=meta.get("ticker"),
            duplicate_of=result.existing_document_ids or None,
            canonical_document_id=canonical,
        )

    # ---------------- vòng lặp chính ----------------

    def run(self) -> None:
        queue: deque[tuple[str, int]] = deque(
            (canonical_url(u), 0) for u in self.adapter.discover_pages()
        )

        while queue:
            if self.cfg.max_documents and self.documents_stored >= self.cfg.max_documents:
                log.info("Đạt max_documents=%d, dừng nguồn %s",
                         self.cfg.max_documents, self.cfg.id)
                break

            url, depth = queue.popleft()
            if url in self.visited or depth > self.cfg.max_depth:
                continue
            self.visited.add(url)

            allowed, reason = self._allowed(url)
            if not allowed:
                log.info("Bỏ qua trang (%s): %s", reason, url)
                self._log_manifest(CrawlStatus.ROBOTS_DENIED, url, reason=reason)
                continue

            crawl_delay = self.robots.crawl_delay(url)
            if crawl_delay:
                self.limiter.bump_delay(crawl_delay)

            try:
                response = self.downloader.get(url)
            except Exception as exc:  # noqa: BLE001
                log.warning("Không tải được trang %s: %s", url, type(exc).__name__)
                log.debug("Chi tiết lỗi trang %s", url, exc_info=exc)
                self._log_manifest(CrawlStatus.TEMPORARY_ERROR, url, error=str(exc)[:300])
                continue

            # Chính trang này đã là file đính kèm.
            if detect_file_type(response) is not None:
                self.handle_candidate(
                    Candidate(url=url, title=filename_from_url(url), source_page_url=url)
                )
                continue

            content_type = response.headers.get("content-type", "").lower()
            if "html" not in content_type and not response.text.lstrip().startswith("<"):
                continue

            candidates, pages = self.adapter.parse_listing(url, response)

            # Trang không có link đính kèm nào có thể là trang xem trước nhúng
            # file thật trong <iframe>/<embed>/<object>.
            if not candidates:
                embedded = resolve_attachment_url(response)
                if embedded:
                    embedded = canonical_url(embedded)
                    if embedded not in self.visited and domain_allowed(
                        embedded, self.cfg.allowed_domains
                    ):
                        candidates = [
                            Candidate(
                                url=embedded,
                                title=filename_from_url(embedded),
                                source_page_url=url,
                            )
                        ]

            # Trang listing không cho ra tài liệu nào có thể là JS-rendered.
            # Phải báo rõ, không im lặng kết thúc với 0 kết quả.
            typed = sum(1 for c in candidates if c.report_type)
            if typed == 0:
                reason = diagnose_empty_listing(
                    response.text, candidates=len(candidates), typed_candidates=typed
                )
                if reason:
                    log.warning(
                        "Trang có vẻ cần render JavaScript, không lấy được tài liệu: %s (%s)",
                        url,
                        reason,
                    )
                    self.js_rendered_pages.append(url)
                    self._log_manifest(
                        CrawlStatus.TEMPORARY_ERROR, url,
                        scope="page", diagnostic="javascript_rendered", reason=reason,
                    )

            for candidate in candidates:
                self.handle_candidate(candidate)

            if depth < self.cfg.max_depth:
                for page in pages:
                    target = canonical_url(page.url)
                    if target not in self.visited:
                        queue.append((target, depth + page.depth_delta))


def crawl_source(
    config: SourceConfig,
    data_dir: Path,
    manifest: ManifestWriter,
    *,
    dry_run: bool = False,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, int]:
    engine = CrawlEngine(config, data_dir, manifest, dry_run=dry_run, transport=transport)
    try:
        engine.run()
    except SourceSkipped as exc:
        # Đây là lý do bug cũ nguy hiểm: trước kia nguồn bị bỏ im lặng.
        log.error("BỎ QUA NGUỒN %s: %s", config.id, exc)
        manifest.write(
            {
                "source_id": config.id,
                "crawl_status": CrawlStatus.TEMPORARY_ERROR.value,
                "url": None,
                "error": str(exc),
                "scope": "source",
            }
        )
    finally:
        counts = engine.db.status_counts()
        engine.close()
    return counts
