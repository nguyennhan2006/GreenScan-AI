"""CLI for the feedback loop and uploaded org packs (feedback-loop-v1, org-pack-v1).

Registered on the main `quantum-agent` app by quantum_gw.cli. Every command is
read-only with respect to verdicts: it exports, measures, proposes, trains into
a new folder, or records a person's decision in an append-only file.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import typer


def _echo_json(data) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def register(app: typer.Typer) -> None:
    @app.command("feedback-bench")
    def feedback_bench(
        export: bool = typer.Option(True, help="Xuất lại ca từ kho quyết định trước khi chạy"),
        update_ratchet: bool = typer.Option(False, "--update-ratchet", help="Thêm ca mới qua vào bánh cóc"),
        cases: Path = typer.Option(Path("benchmark/gs_feedback/cases.jsonl")),
        ratchet: Path = typer.Option(Path("benchmark/gs_feedback/ratchet.json")),
        note: str = typer.Option("", help="Ghi chú cho lần cập nhật bánh cóc"),
    ) -> None:
        """GS-Feedback: chạy lại mọi quyết định đã chốt trên bằng chứng đã chụp; ca đã qua không được hỏng lại."""
        from quantum_gw.feedback.bench import check_ratchet, export_from_store, read_cases, run_cases

        if export:
            path, n = export_from_store(path=cases)
            typer.echo(f"Đã xuất {n} ca vào {path}")
        report = check_ratchet(run_cases(read_cases(cases)), ratchet, update=update_ratchet, note=note)
        _echo_json(report)
        if report["regressions"]:
            typer.echo(f"HỒI QUY: {len(report['regressions'])} ca từng qua nay hỏng.")
            raise typer.Exit(code=1)

    @app.command("feedback-mine")
    def feedback_mine(
        out: Path = typer.Option(Path(".quantum/feedback/proposals")),
        measure: bool = typer.Option(False, help="Đo từng cụm từ đề xuất trên GS-Feedback"),
        bench_limit: int = typer.Option(0, help="Đo thêm trên N ca GS-Bench đầu (0 = không)"),
    ) -> None:
        """Máy đào luật: gom quyết định ghi đè thành phiếu đề xuất (cụm từ, quy tắc, truy xuất, org pack)."""
        from quantum_gw.feedback.bench import build_cases
        from quantum_gw.feedback.hygiene import QAStore
        from quantum_gw.feedback.miner import measure_cue, mine, write_sheet
        from quantum_gw.storage.reviews import ReviewStore

        proposals = mine()
        if measure and proposals["cues"]:
            store = ReviewStore()
            cases = build_cases(store.gold_records(), QAStore(reviews=store).all())
            for cue in proposals["cues"]:
                cue["measured"] = measure_cue(cue["term"], cue["family"], cases, bench_limit)
        md, js = write_sheet(proposals, out)
        typer.echo(f"Phiếu đề xuất: {md}\nDữ liệu: {js}")
        typer.echo(f"{len(proposals['cues'])} cụm từ, {len(proposals['rules'])} quy tắc, "
                   f"{len(proposals['queries'])} ca truy xuất, {len(proposals['org_rules'])} quy tắc nội bộ nháp.")

    @app.command("feedback-dataset")
    def feedback_dataset(
        out: Path = typer.Option(Path(".quantum/feedback/stance_pairs.jsonl")),
        claude: bool = typer.Option(True, help="Gộp 821 cặp Claude gán nhãn (deploy/vastai_a100/data)"),
        scope: str = typer.Option("core", help="core, hoặc org:<org_id>"),
    ) -> None:
        """Xuất cặp (tuyên bố, đoạn, quan hệ) đã lọc nhãn để huấn luyện mô hình lập trường."""
        from quantum_gw.feedback.dataset import build, write

        info = write(build(scope=scope, include_claude=claude), out)
        typer.echo(f"Đã ghi {out}")
        _echo_json(info)

    @app.command("feedback-train")
    def feedback_train(
        data: Path = typer.Option(Path(".quantum/feedback/stance_pairs.jsonl")),
        out_dir: Path = typer.Option(Path("models/stance")),
        trained_by: str = typer.Option(..., help="Tên người huấn luyện (không được tự duyệt)"),
        c: float = typer.Option(4.0, help="Độ mạnh điều chuẩn nghịch đảo"),
        registry_file: Path = typer.Option(Path("models/stance/registry.json")),
    ) -> None:
        """Huấn luyện mô hình thách đấu (CPU), chấm cùng nhà vô địch (luật) trên tập giữ lại, ghi vào sổ."""
        from quantum_gw.feedback.dataset import manifest, read
        from quantum_gw.feedback.registry import register
        from quantum_gw.feedback.stance_model import KIND, challenger_metrics, champion_metrics, train

        pairs = read(data)
        model = train(pairs, c=c)
        holdout = [p for p in pairs if p.get("split") == "holdout" and p.get("champion")]
        folder = out_dir / f"hl-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
        model.meta["data"] = manifest(pairs)
        model.save(folder)
        entry = register(registry_file, folder, champion=champion_metrics(holdout),
                         challenger=challenger_metrics(model, holdout), data=manifest(pairs),
                         trained_by=trained_by, kind=KIND)
        typer.echo(f"Mô hình: {folder}")
        _echo_json({"gate": entry["gate"], "champion": entry["champion"], "challenger": entry["challenger"]})

    @app.command("feedback-promote")
    def feedback_promote(
        model_id: str = typer.Argument(...),
        approved_by: str = typer.Option(..., help="Người duyệt, khác người huấn luyện"),
        registry_file: Path = typer.Option(Path("models/stance/registry.json")),
    ) -> None:
        """Thăng hạng một mô hình đã qua cổng; mô hình đang dùng trước đó bị cho nghỉ."""
        from quantum_gw.feedback.registry import promote

        try:
            entry = promote(registry_file, model_id, approved_by)
        except ValueError as exc:
            typer.echo(f"Từ chối: {exc}")
            raise typer.Exit(code=1) from None
        typer.echo(f"Đã thăng hạng {entry['model_id']} (duyệt bởi {entry['approved_by']}). "
                   f"Bật bằng QUANTUM_LOCAL_STANCE_MODEL={entry['path']}")

    @app.command("feedback-qa")
    def feedback_qa(
        action: str = typer.Argument(..., help="sample | agreement"),
        rate: float = typer.Option(0.10),
        seed: str = typer.Option("", help="Mặc định tháng hiện tại, ví dụ 2026-11"),
    ) -> None:
        """Lấy mẫu cho người soát thứ hai, hoặc báo độ đồng thuận (kappa) và các ca chờ trọng tài."""
        from quantum_gw.feedback.hygiene import QAStore, agreement, sample_for_second_review
        from quantum_gw.storage.reviews import ReviewStore

        store = ReviewStore()
        gold = store.gold_records()
        if action == "sample":
            _echo_json(sample_for_second_review(gold, rate, seed))
        elif action == "agreement":
            _echo_json(agreement(gold, QAStore(reviews=store).all()))
        else:
            raise typer.BadParameter("action phải là sample hoặc agreement")

    @app.command("org-upload")
    def org_upload(
        path: Path = typer.Argument(..., help="Thư mục pack hoặc tệp .zip"),
        uploaded_by: str = typer.Option(..., "--by"),
    ) -> None:
        """Đưa một org pack vào kho tải lên (luôn là bản nháp; cần người khác duyệt)."""
        from quantum_gw.legal.org_registry import ingest

        if path.is_dir():
            files = [(str(f.relative_to(path)).replace("\\", "/"), f.read_bytes()) for f in path.rglob("*") if f.is_file()]
        else:
            files = [(path.name, path.read_bytes())]
        result = ingest(files, uploaded_by)
        _echo_json(result)
        if result["status"] != "draft":
            raise typer.Exit(code=1)

    @app.command("org-approve")
    def org_approve(org_id: str, version: str, approved_by: str = typer.Option(..., "--by"),
                    comment: str = typer.Option("")) -> None:
        """Duyệt một pack nháp trong kho tải lên (người duyệt phải khác người tải lên)."""
        from quantum_gw.legal.org_registry import approve

        try:
            _echo_json(approve(org_id, version, approved_by, comment))
        except ValueError as exc:
            typer.echo(f"Từ chối: {exc}")
            raise typer.Exit(code=1) from None

    @app.command("org-draft")
    def org_draft(
        policy: Path = typer.Argument(..., help="Văn bản chính sách (.md, .txt)"),
        org_id: str = typer.Option(...), org_name: str = typer.Option(...),
        org_type: str = typer.Option("other"), out: Path = typer.Option(None, help="Mặc định configs/org_packs/<org_id>_nhap"),
        llm: bool = typer.Option(False, help="Để mô hình soạn (cần nhà cung cấp cho legal_reasoning)"),
    ) -> None:
        """Soạn bản nháp org pack từ văn bản chính sách: mỗi câu nêu nghĩa vụ thành một quy tắc, dẫn đúng điều khoản."""
        from quantum_gw.legal.org_draft import draft, write

        text = policy.read_text(encoding="utf-8")
        result = draft(text, org_id, org_name, org_type, use_llm=llm)
        folder = write(out or Path("configs/org_packs") / f"{org_id}_nhap" / org_id, result["pack"], text)
        typer.echo(f"Bản nháp ({result['method']}, {len(result['pack']['rules'])} quy tắc): {folder}")
        for note in result["notes"]:
            typer.echo(f"  - {note}")
        for error in result["errors"]:
            typer.echo(f"  LỖI: {error}")
        if result["errors"]:
            raise typer.Exit(code=1)


if __name__ == "__main__":  # pragma: no cover
    sys.exit("dùng: quantum-agent <lệnh>")
