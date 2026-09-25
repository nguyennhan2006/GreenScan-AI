from __future__ import annotations

import json
from pathlib import Path

from quantum_gw.domain.models import AnalysisResult


class ReportingAgent:
    def write(self, result: AnalysisResult) -> None:
        output = Path(result.output_directory)
        output.mkdir(parents=True, exist_ok=True)
        (output / "result.json").write_text(
            json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        (output / "evidence_pack.md").write_text(self._markdown(result), encoding="utf-8")

    def _queue_section(self, result: AnalysisResult) -> list[str]:
        """Where to start, why, and what this pass left alone."""
        if not result.priorities:
            return []
        claims = {claim.claim_id: claim for claim in result.claims}
        status = {v.claim.claim_id: v.status for v in result.verifications}
        queued = sorted(
            (p for p in result.priorities if p.get("in_queue")),
            key=lambda p: p.get("rank", 0),
        )
        lines = ["", "## Review queue — start here", ""]
        for item in queued:
            claim = claims.get(item["claim_id"])
            if claim is None:
                continue
            page = f"p.{claim.source_page}" if claim.source_page is not None else "—"
            lines.append(
                f"{item['rank']}. **{item['priority_score']:.0f}/100** · {page} · "
                f"`{status.get(claim.claim_id, '')}` — {claim.text[:160]}"
            )
            for reason in item.get("reasons", []):
                lines.append(f"   - {reason}")
        lines.extend(["", "### Scope of this pass", "", result.scope_note, ""])
        return lines

    def _markdown(self, result: AnalysisResult) -> str:
        lines = [
            "# Greenwashing-risk evidence pack",
            "",
            f"- Run ID: `{result.run_id}`",
            f"- Pipeline: `{result.manifest.pipeline_version}`",
            f"- Release status: **{result.summary.release_status}**",
            f"- Claims: {result.summary.total_claims}",
            "",
            "## Quality gates",
            "",
        ]
        for gate in result.quality_gates:
            lines.append(f"- **{gate.gate_id} {gate.name}: {gate.status}** — {gate.details}")

        # The work list comes before the claim dump: an auditor opens this file to
        # find out where to start, not to read 156 entries in document order.
        lines.extend(self._queue_section(result))

        lines.extend(["", "## Claim assessments", ""])
        risk_by_claim = {risk.claim_id: risk for risk in result.risks}
        for index, verification in enumerate(result.verifications, start=1):
            risk = risk_by_claim[verification.claim.claim_id]
            lines.extend(
                [
                    f"### {index}. {verification.claim.text}",
                    "",
                    f"- Type: `{verification.claim.claim_type}`",
                    f"- Verification: **{verification.status}**",
                    f"- Risk: **{risk.risk_score}/100 ({risk.severity})**",
                    f"- Rationale: {verification.rationale}",
                    "- Evidence:",
                ]
            )
            if verification.evidence:
                for item in verification.evidence:
                    excerpt = item.text.replace("\n", " ")[:350]
                    lines.append(f"  - `{item.citation}` (score {item.score:.3f}): {excerpt}")
            else:
                lines.append("  - No admissible evidence.")
            if verification.warnings:
                lines.append("- Warnings: " + "; ".join(verification.warnings))
            lines.append("")
        lines.extend(
            [
                "## Interpretation notice",
                "",
                "This is a screening result, not a legal conclusion. Missing evidence is distinct from contradiction. High-risk outputs require human review.",
            ]
        )
        return "\n".join(lines)
