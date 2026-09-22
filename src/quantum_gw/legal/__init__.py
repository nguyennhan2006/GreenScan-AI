"""Legal knowledge layer: L0 originals -> L1 clauses -> L2 temporal graph -> L3 rules."""

from .checker import LegalChecker, LegalCheckResult
from .corpus import CURRENT, HISTORICAL, LegalCorpus, LegalDocument
from .gates import GateResult, audit_corpus, audit_rules, check_rule, check_source
from .parser import Clause, parse_document, structure_summary
from .rules import RulePack, combine, evaluate_condition

__all__ = [
    "Clause", "parse_document", "structure_summary",
    "LegalCorpus", "LegalDocument", "HISTORICAL", "CURRENT",
    "RulePack", "evaluate_condition", "combine",
    "LegalChecker", "LegalCheckResult",
    "GateResult", "check_source", "check_rule", "audit_corpus", "audit_rules",
]
