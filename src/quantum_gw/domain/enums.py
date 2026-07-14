from enum import StrEnum


class DocumentRole(StrEnum):
    CLAIM_SOURCE = "claim_source"
    EVIDENCE = "evidence"
    REFERENCE = "reference"


class SourceType(StrEnum):
    INTERNAL = "internal"
    FINANCIAL = "financial"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"
    EXTERNAL = "external"
    STANDARD = "standard"


class VerificationStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
