from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .engine import crawl_source
from .pipeline.manifest import ManifestWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Thu thập báo cáo doanh nghiệp Việt Nam")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--source", action="append", help="Chỉ chạy source id này (lặp được)")
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="Chạy cả nguồn có enabled: false (dùng cho dry-run kiểm thử)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Chỉ phát hiện, không tải file")
    parser.add_argument("--max-documents", type=int, help="Ghi đè max_documents cho mọi nguồn")
    parser.add_argument("--log-level", default="INFO")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    log = logging.getLogger("crawler")

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        log.error("Cấu hình không hợp lệ:\n%s", exc)
        return 2

    sources = config.sources
    if args.source:
        wanted = set(args.source)
        sources = [s for s in sources if s.id in wanted]
        missing = wanted - {s.id for s in sources}
        if missing:
            log.error("Không tìm thấy source: %s", sorted(missing))
            return 2

    if not args.include_disabled and not args.dry_run:
        disabled = [s.id for s in sources if not s.enabled]
        sources = [s for s in sources if s.enabled]
        if disabled:
            log.info(
                "Bỏ qua nguồn chưa bật: %s (dùng --include-disabled hoặc --dry-run để chạy thử)",
                sorted(disabled),
            )

    if not sources:
        log.error("Không có nguồn nào để chạy")
        return 2

    if args.max_documents:
        sources = [s.model_copy(update={"max_documents": args.max_documents}) for s in sources]

    exit_code = 0
    with ManifestWriter(args.data_dir) as manifest:
        log.info("Manifest: %s", manifest.path)
        for source in sources:
            log.info("=== %s (%s / %s) ===", source.id, source.adapter, source.authority.value)
            try:
                crawl_source(source, args.data_dir, manifest, dry_run=args.dry_run)
            except Exception:
                log.exception("Nguồn %s thất bại", source.id)
                exit_code = 1
        log.info("Tổng kết manifest: %s", manifest.summary())

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
