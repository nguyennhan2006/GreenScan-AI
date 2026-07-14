from __future__ import annotations

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import (
    AnalysisResult,
    ClaimSuggestion,
    RiskAssessment,
    SuggestionItem,
    VerificationResult,
)


class SuggestionAgent:
    """Turns verification and risk findings into actionable edit suggestions per claim."""

    def run(self, result: AnalysisResult) -> list[ClaimSuggestion]:
        risk_by_claim = {risk.claim_id: risk for risk in result.risks}
        suggestions = []
        for verification in result.verifications:
            risk = risk_by_claim.get(verification.claim.claim_id)
            if risk is None:
                continue
            suggestions.append(self._suggest(verification, risk))
        return suggestions

    def _suggest(self, verification: VerificationResult, risk: RiskAssessment) -> ClaimSuggestion:
        claim = verification.claim
        items: list[SuggestionItem] = []

        if claim.is_vague or not claim.metric:
            items.append(
                SuggestionItem(
                    code="vague_claim",
                    issue="Tuyên bố mơ hồ hoặc thiếu chỉ số đo lường cụ thể.",
                    recommendation="Nêu rõ chỉ số môi trường (CO2, năng lượng, nước, chất thải...) và cách đo lường.",
                    example_fix="Thay 'thân thiện với môi trường' bằng 'giảm 12% phát thải CO2 phạm vi 1 và 2 trong năm 2024 so với 2023'.",
                )
            )
        if not claim.values:
            items.append(
                SuggestionItem(
                    code="missing_quantitative_value",
                    issue="Tuyên bố không có số liệu định lượng.",
                    recommendation="Bổ sung con số cụ thể kèm đơn vị (%, tấn CO2e, kWh, m3...).",
                )
            )
        if (claim.direction or claim.is_future_commitment) and not claim.baseline:
            items.append(
                SuggestionItem(
                    code="missing_baseline",
                    issue="Tuyên bố tăng/giảm hoặc cam kết tương lai nhưng thiếu năm cơ sở (baseline).",
                    recommendation="Nêu rõ năm cơ sở so sánh, ví dụ 'so với mức năm 2020'.",
                )
            )
        if not claim.period:
            items.append(
                SuggestionItem(
                    code="missing_period",
                    issue="Thiếu kỳ báo cáo hoặc mốc thời gian của tuyên bố.",
                    recommendation="Bổ sung kỳ báo cáo (ví dụ 'năm tài chính 2024') hoặc hạn hoàn thành cam kết.",
                )
            )

        if verification.status == VerificationStatus.CONTRADICTED:
            citations = ", ".join(e.citation for e in verification.evidence[:2]) or "nguồn chứng cứ"
            items.append(
                SuggestionItem(
                    code="contradicted_by_evidence",
                    issue=f"Tuyên bố mâu thuẫn với chứng cứ: {citations}.",
                    recommendation="Đối chiếu lại số liệu với tài liệu nguồn và sửa tuyên bố hoặc bổ sung giải trình chênh lệch.",
                )
            )
        elif verification.status in {
            VerificationStatus.UNSUPPORTED,
            VerificationStatus.INSUFFICIENT_EVIDENCE,
        }:
            items.append(
                SuggestionItem(
                    code="missing_evidence",
                    issue="Chưa tìm thấy chứng cứ đủ mạnh cho tuyên bố trong tài liệu cung cấp.",
                    recommendation="Đính kèm tài liệu chứng minh (báo cáo kiểm toán, số liệu đo đạc, chứng nhận) hoặc điều chỉnh phạm vi tuyên bố.",
                )
            )
        elif verification.status == VerificationStatus.PARTIALLY_SUPPORTED:
            items.append(
                SuggestionItem(
                    code="partial_evidence",
                    issue="Chứng cứ chỉ hỗ trợ một phần tuyên bố.",
                    recommendation="Thu hẹp tuyên bố về đúng phạm vi được chứng minh hoặc bổ sung chứng cứ cho phần còn thiếu.",
                )
            )

        independent = any(
            e.source_type.value in {"legal", "external", "standard"} for e in verification.evidence
        )
        if not independent:
            items.append(
                SuggestionItem(
                    code="no_independent_source",
                    issue="Thiếu nguồn xác nhận độc lập (pháp lý, bên thứ ba, tiêu chuẩn).",
                    recommendation="Bổ sung chứng nhận/kiểm định của bên thứ ba hoặc dẫn chiếu tiêu chuẩn áp dụng (ISO 14064, GHG Protocol...).",
                )
            )

        for warning in verification.warnings:
            items.append(
                SuggestionItem(
                    code="verifier_warning",
                    issue=warning,
                    recommendation="Xem lại cảnh báo của bước xác minh và xử lý trước khi công bố.",
                )
            )

        return ClaimSuggestion(
            claim_id=claim.claim_id,
            claim_text=claim.text,
            status=verification.status,
            severity=risk.severity,
            risk_score=risk.risk_score,
            items=items,
        )
