"""Object store tách khỏi document path -> dedupe không làm hỏng provenance."""

from __future__ import annotations

from conftest import PDF_A, PDF_B
from crawler.models import CrawlStatus
from crawler.pipeline.deduplicator import Deduplicator
from crawler.storage.database import Database
from crawler.storage.object_store import ObjectStore, make_document_id


def build(tmp_path):
    db = Database(tmp_path)
    store = ObjectStore(tmp_path)
    return db, store, Deduplicator(store, db)


def test_object_path_is_content_addressed(tmp_path):
    _, store, _ = build(tmp_path)
    sha, path, is_new = store.put_object(PDF_A, ".pdf")
    assert is_new is True
    assert path.name == f"{sha}.pdf"
    assert path.parent.name == sha[:2]

    _, path2, is_new2 = store.put_object(PDF_A, ".pdf")
    assert is_new2 is False and path2 == path


def test_duplicate_content_keeps_separate_documents(tmp_path):
    """Regression: bản cũ khiến local_path của báo cáo này trỏ sang tên file báo cáo khác."""
    db, store, dedup = build(tmp_path)

    annual_id = make_document_id("s1", "HPG", 2023, "annual", "http://x.test/a.pdf")
    sustain_id = make_document_id("s1", "HPG", 2024, "sustainability", "http://x.test/b.pdf")

    for doc_id, url, year, rtype in [
        (annual_id, "http://x.test/a.pdf", 2023, "annual"),
        (sustain_id, "http://x.test/b.pdf", 2024, "sustainability"),
    ]:
        db.upsert_discovery(doc_id, {
            "source_id": "s1", "ticker": "HPG", "year": year,
            "report_type": rtype, "file_url": url, "source_authority": "aggregator",
        })

    first = dedup.store_content(PDF_A, ".pdf")
    db.mark_downloaded("http://x.test/a.pdf", first.sha256, "pdf", "a.pdf")

    second = dedup.store_content(PDF_A, ".pdf")   # nội dung y hệt
    db.mark_downloaded("http://x.test/b.pdf", second.sha256, "pdf", "b.pdf", duplicate=True)

    assert first.sha256 == second.sha256
    assert second.is_duplicate is True

    # Hai document riêng biệt, giữ nguyên year/report_type/filename của chính mình.
    annual = db.get_document("http://x.test/a.pdf")
    sustain = db.get_document("http://x.test/b.pdf")
    assert annual["year"] == 2023 and annual["report_type"] == "annual"
    assert sustain["year"] == 2024 and sustain["report_type"] == "sustainability"
    assert annual["original_filename"] == "a.pdf"
    assert sustain["original_filename"] == "b.pdf"
    # ...nhưng dùng chung một object trên đĩa.
    assert annual["object_sha256"] == sustain["object_sha256"]
    assert len(list(tmp_path.glob("objects/sha256/*/*.pdf"))) == 1


def test_canonical_document_prefers_highest_authority(tmp_path):
    db, _, dedup = build(tmp_path)
    entries = [
        ("mirror", "http://m.test/x.pdf", "mirror"),
        ("official", "http://o.test/x.pdf", "official_exchange"),
        ("agg", "http://a.test/x.pdf", "aggregator"),
    ]
    for source_id, url, authority in entries:
        doc_id = make_document_id(source_id, "HPG", 2024, "annual", url)
        db.upsert_discovery(doc_id, {
            "source_id": source_id, "file_url": url, "source_authority": authority,
            "ticker": "HPG", "year": 2024, "report_type": "annual",
        })
        result = dedup.store_content(PDF_B, ".pdf")
        db.mark_downloaded(url, result.sha256, "pdf", "x.pdf")

    sha = ObjectStore.digest(PDF_B)
    canonical = dedup.canonical_document(sha)
    assert canonical is not None and canonical.startswith("official:")


def test_canonical_is_written_to_every_document_in_group(tmp_path):
    """Canonical là thuộc tính của nhóm -> mọi document cùng object phải trỏ về nó."""
    db, _, dedup = build(tmp_path)
    urls = [
        ("mirror", "http://m.test/x.pdf", "mirror"),
        ("official", "http://o.test/x.pdf", "official_exchange"),
    ]
    for source_id, url, authority in urls:
        doc_id = make_document_id(source_id, "HPG", 2024, "annual", url)
        db.upsert_discovery(doc_id, {
            "source_id": source_id, "file_url": url, "source_authority": authority,
            "ticker": "HPG", "year": 2024, "report_type": "annual",
        })
        result = dedup.store_content(PDF_B, ".pdf")
        db.mark_downloaded(url, result.sha256, "pdf", "x.pdf")
        dedup.refresh_canonical(result.sha256)

    canonical = db.get_document("http://o.test/x.pdf")["canonical_document_id"]
    assert canonical.startswith("official:")
    # Bản mirror -- được ghi TRƯỚC khi bản official xuất hiện -- vẫn phải cập nhật.
    assert db.get_document("http://m.test/x.pdf")["canonical_document_id"] == canonical


def test_canonical_stable_when_new_mirror_arrives(tmp_path):
    """Thêm mirror mới không được làm đổi canonical đã chọn."""
    db, _, dedup = build(tmp_path)

    first_url = "http://a.test/x.pdf"
    db.upsert_discovery(make_document_id("agg_a", "HPG", 2024, "annual", first_url), {
        "source_id": "agg_a", "file_url": first_url, "source_authority": "aggregator",
        "ticker": "HPG", "year": 2024, "report_type": "annual",
    })
    result = dedup.store_content(PDF_A, ".pdf")
    db.mark_downloaded(first_url, result.sha256, "pdf", "x.pdf")
    before = dedup.refresh_canonical(result.sha256)

    second_url = "http://b.test/x.pdf"
    db.upsert_discovery(make_document_id("agg_b", "HPG", 2024, "annual", second_url), {
        "source_id": "agg_b", "file_url": second_url, "source_authority": "aggregator",
        "ticker": "HPG", "year": 2024, "report_type": "annual",
    })
    db.mark_downloaded(second_url, result.sha256, "pdf", "x.pdf", duplicate=True)
    after = dedup.refresh_canonical(result.sha256)

    assert before == after, "canonical phải ổn định khi cùng authority"


def test_should_skip_only_when_object_present(tmp_path):
    db, _, dedup = build(tmp_path)
    url = "http://x.test/a.pdf"
    doc_id = make_document_id("s1", "HPG", 2024, "annual", url)
    db.upsert_discovery(doc_id, {"source_id": "s1", "file_url": url})

    assert db.should_skip(url) is False           # mới discovered
    db.mark_status(url, CrawlStatus.NOT_FOUND)
    assert db.should_skip(url) is False           # 404 -> vẫn thử lại lần sau

    result = dedup.store_content(PDF_A, ".pdf")
    db.mark_downloaded(url, result.sha256, "pdf", "a.pdf")
    assert db.should_skip(url) is True            # đã tải xong

    result.path.unlink()
    assert db.should_skip(url) is False           # file mất -> tải lại


def test_error_state_is_recorded(tmp_path):
    db, _, _ = build(tmp_path)
    url = "http://x.test/missing.pdf"
    db.upsert_discovery(make_document_id("s1", None, None, None, url),
                        {"source_id": "s1", "file_url": url})
    db.mark_status(url, CrawlStatus.NOT_FOUND, error_code="404", error_message="not found")

    row = db.get_document(url)
    assert row["crawl_status"] == "not_found"
    assert row["attempt_count"] == 1
    assert row["last_error_code"] == "404"
    assert row["last_attempt_at"]
