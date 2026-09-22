"""End-to-end trên fixture site: query-string URL, redirect, 404, duplicate, robots."""

from __future__ import annotations

import json

from conftest import FixtureSite
from crawler.engine import crawl_source
from crawler.models import RobotsPolicy, SourceAuthority, SourceConfig
from crawler.pipeline.manifest import ManifestWriter
from crawler.storage.database import Database


def make_config(**overrides) -> SourceConfig:
    base = dict(
        id="fixture",
        adapter="generic_html",
        company="Fixture JSC",
        authority=SourceAuthority.AGGREGATOR,
        enabled=True,
        start_urls=["http://x.test/"],
        allowed_domains=["x.test"],
        allowed_file_types=["pdf", "xlsx"],
        attachment_patterns=["/Handlers/DownloadAttachedFile.ashx", "/redirect/"],
        exclude_patterns=["tuyển dụng"],
        delay_seconds=0.0,
        max_depth=2,
        report_types={
            "sustainability": ["báo cáo phát triển bền vững"],
            "annual": ["báo cáo thường niên"],
            "financial": ["báo cáo tài chính"],
            "governance": ["báo cáo quản trị"],
        },
    )
    base.update(overrides)
    return SourceConfig(**base)


def run(site: FixtureSite, data_dir, **overrides):
    with ManifestWriter(data_dir) as manifest:
        crawl_source(make_config(**overrides), data_dir, manifest,
                     transport=site.transport())
        path = manifest.path
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return Database(data_dir), records


def test_full_crawl(site: FixtureSite, data_dir):
    db, records = run(site, data_dir)
    by_status = {}
    for record in records:
        by_status.setdefault(record["crawl_status"], []).append(record)

    downloaded = {r["url"] for r in by_status.get("downloaded", [])}
    # PDF thường
    assert "http://x.test/files/ptbv-2024.pdf" in downloaded
    # .ashx: URL không có đuôi, nhận ra nhờ magic bytes
    assert "http://x.test/Handlers/DownloadAttachedFile.ashx?NewsID=99&FileName=btn-2023.pdf" in downloaded
    # query-string trả về XLSX
    assert "http://x.test/download?file=bctc-q1-2024.xlsx" in downloaded

    # Loại trừ hoạt động
    assert not any("tuyen-dung" in r["url"] for r in records)


def test_404_recorded_and_not_retried(site: FixtureSite, data_dir):
    db, records = run(site, data_dir)
    missing = [r for r in records if r["url"].endswith("missing-2022.pdf")]
    assert missing and missing[0]["crawl_status"] == "not_found"
    # Chỉ gọi đúng một lần, không retry 3 lần như bản cũ.
    assert site.hits["/files/missing-2022.pdf"] == 1

    row = db.get_document("http://x.test/files/missing-2022.pdf")
    assert row["crawl_status"] == "not_found"
    assert row["last_error_code"] == "404"


def test_duplicate_content_shares_object_not_identity(site: FixtureSite, data_dir):
    db, records = run(site, data_dir)
    original = db.get_document("http://x.test/files/ptbv-2024.pdf")
    mirror = db.get_document("http://x.test/files/ptbv-2024-mirror.pdf")

    assert original["object_sha256"] == mirror["object_sha256"]
    assert mirror["crawl_status"] == "duplicate"
    # Tên file gốc của mỗi document được giữ riêng.
    assert original["original_filename"] == "ptbv-2024.pdf"
    assert mirror["original_filename"] == "ptbv-2024-mirror.pdf"
    # Chỉ một bản bytes trên đĩa.
    objects = list(data_dir.glob("objects/sha256/*/*.pdf"))
    shas = {p.stem for p in objects}
    assert original["object_sha256"] in shas


def test_redirect_followed_to_real_file(site: FixtureSite, data_dir):
    db, records = run(site, data_dir)
    row = db.get_document("http://x.test/redirect/governance")
    assert row is not None and row["crawl_status"] in ("downloaded", "duplicate")
    assert row["file_format"] == "pdf"


def test_iframe_viewer_resolved(site: FixtureSite, data_dir):
    """Trang xem trước nhúng iframe -> phải lần ra file thật bên trong."""
    db, records = run(site, data_dir)
    assert db.get_document("http://x.test/files/btn-2020.pdf") is not None


def test_robots_disallow_is_respected(site: FixtureSite, data_dir):
    db, records = run(site, data_dir, start_urls=["http://x.test/private/secret.pdf"])
    assert any(r["crawl_status"] == "robots_denied" for r in records)
    assert "/private/secret.pdf" not in site.hits


def test_robots_network_failure_skips_source_loudly(data_dir):
    """Nguồn phải được ghi nhận là bỏ qua, không im lặng như bản cũ."""
    site = FixtureSite(robots_error=True)
    db, records = run(
        site, data_dir,
        robots_policy=RobotsPolicy(on_temporary_error="retry_then_skip", retry_attempts=2),
    )
    source_level = [r for r in records if r.get("scope") == "source"]
    assert source_level, "phải có bản ghi manifest cấp nguồn khi bỏ qua"
    assert "robots.txt" in source_level[0]["error"]
    # Không tải bất kỳ file nào.
    assert not any(r["crawl_status"] == "downloaded" for r in records)


def test_dry_run_downloads_nothing(site: FixtureSite, data_dir):
    db, records = run(site, data_dir, id="fixture")  # chạy thật để có baseline
    assert any(r["crawl_status"] == "downloaded" for r in records)

    site2 = FixtureSite()
    data_dir2 = data_dir.parent / "dry"
    with ManifestWriter(data_dir2) as manifest:
        crawl_source(make_config(), data_dir2, manifest, dry_run=True,
                     transport=site2.transport())
        records2 = [json.loads(line) for line in
                    manifest.path.read_text(encoding="utf-8").splitlines()]

    assert all(r["crawl_status"] == "discovered" for r in records2)
    assert not list(data_dir2.glob("objects/sha256/*/*"))


def test_manifest_written_with_run_id(site: FixtureSite, data_dir):
    with ManifestWriter(data_dir) as manifest:
        crawl_source(make_config(), data_dir, manifest, transport=site.transport())
        assert manifest.path.parent.name == "manifests"
        assert manifest.path.name.startswith("crawl-")
        assert manifest.summary()

    records = [json.loads(line) for line in
               manifest.path.read_text(encoding="utf-8").splitlines()]
    assert all("run_id" in r and "logged_at" in r for r in records)


def test_max_documents_stops_early(site: FixtureSite, data_dir):
    db, records = run(site, data_dir, max_documents=1)
    stored = [r for r in records if r["crawl_status"] in ("downloaded", "duplicate")]
    assert len(stored) == 1


def test_rerun_skips_already_downloaded(site: FixtureSite, data_dir):
    run(site, data_dir)
    first_hits = site.hits["/files/ptbv-2024.pdf"]

    site2 = FixtureSite()
    run(site2, data_dir)
    assert first_hits == 1
    assert "/files/ptbv-2024.pdf" not in site2.hits, "không được tải lại file đã có"
