from __future__ import annotations

import re
from pathlib import Path

import yaml

from quantum_gw.domain.enums import DocumentRole
from quantum_gw.domain.models import Claim, EvidenceChunk
from quantum_gw.settings import ClaimSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import YEAR_RE, normalize_for_match, parse_numbers, split_sentences, stable_id


class ClaimExtractionAgent:
    def __init__(self, settings: ClaimSettings, audit: AuditLogger, taxonomy_path: str = "configs/taxonomy_vi.yaml"):
        self.settings = settings
        self.audit = audit
        path = Path(taxonomy_path)
        if not path.exists():
            path = Path(__file__).resolve().parents[3] / taxonomy_path
        self.taxonomy = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.claim_types: dict[str, dict] = self.taxonomy["claim_types"]
        patterns = self.taxonomy["risk_patterns"]
        self.vague_terms = [normalize_for_match(term) for term in patterns["vague_terms"]]
        self.reduction_terms = [normalize_for_match(term) for term in patterns["reduction_terms"]]
        self.increase_terms = [normalize_for_match(term) for term in patterns["increase_terms"]]
        self.future_terms = [normalize_for_match(term) for term in patterns["future_terms"]]

    def run(self, chunks: list[EvidenceChunk]) -> list[Claim]:
        claims: list[Claim] = []
        seen: set[str] = set()
        for chunk in chunks:
            if chunk.role != DocumentRole.CLAIM_SOURCE:
                continue
            for sentence in split_sentences(chunk.text):
                normalized = normalize_for_match(sentence)
                claim_type = self._claim_type(normalized)
                if not claim_type:
                    continue
                numbers = parse_numbers(sentence)
                is_vague = any(term in normalized for term in self.vague_terms) and not numbers
                if is_vague and not self.settings.include_vague_claims:
                    continue
                confidence = min(0.96, 0.48 + (0.18 if numbers else 0) + (0.12 if claim_type != "generic_sustainability" else 0))
                if confidence < self.settings.minimum_confidence:
                    continue
                canonical = re.sub(r"\s+", " ", normalized).strip()
                if canonical in seen:
                    continue
                seen.add(canonical)
                years = YEAR_RE.findall(sentence)
                direction = None
                if any(term in normalized for term in self.reduction_terms):
                    direction = "decrease"
                elif any(term in normalized for term in self.increase_terms):
                    direction = "increase"
                metric = self._metric(normalized)
                claim = Claim(
                    claim_id=stable_id(chunk.chunk_id, sentence),
                    text=sentence,
                    claim_type=claim_type,
                    source_chunk_id=chunk.chunk_id,
                    source_name=chunk.source_name,
                    source_page=chunk.page,
                    metric=metric,
                    direction=direction,
                    values=[value for value, _ in numbers],
                    units=[unit for _, unit in numbers if unit],
                    period=years[0] if years else None,
                    baseline=years[-1] if len(years) > 1 else None,
                    is_future_commitment=any(term in normalized for term in self.future_terms),
                    is_vague=is_vague,
                    confidence=confidence,
                )
                claims.append(claim)
        self.audit.write("claims_extracted", {"count": len(claims)})
        return claims

    def _claim_type(self, normalized: str) -> str | None:
        best: tuple[str, int] | None = None
        for name, config in self.claim_types.items():
            hits = sum(1 for keyword in config["keywords"] if normalize_for_match(keyword) in normalized)
            if hits and (best is None or hits > best[1]):
                best = (name, hits)
        return best[0] if best else None

    @staticmethod
    def _metric(normalized: str) -> str | None:
        mapping = {
            "emissions": ["phat thai", "carbon", "co2", "ghg"],
            "renewable_energy": ["nang luong tai tao", "dien mat troi", "dien gio"],
            "energy": ["nang luong", "dien nang"],
            "water": ["nuoc"],
            "waste": ["chat thai", "tai che"],
            "green_finance": ["trai phieu xanh", "tin dung xanh", "green bond", "green loan"],
        }
        for metric, terms in mapping.items():
            if any(term in normalized for term in terms):
                return metric
        return None
