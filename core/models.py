from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    CRITICO = "CRITICO"
    AVISO = "AVISO"
    INFO = "INFO"


class ChangeType(str, Enum):
    MODIFIED = "modified"
    MISSING = "missing"
    ADDED = "added"


class DiscoveryMethod(str, Enum):
    TOC = "toc"
    HEURISTIC = "heuristic"
    AI = "ai"
    NONE = "none"


@dataclass
class StructuralResult:
    expected_sections: list[str]
    found_sections: list[str]
    missing_sections: list[str]
    score: float
    discovery_method: DiscoveryMethod


@dataclass
class SemanticDiscrepancy:
    location: int | str  # número de página (PDF) o "Párrafo N" (DOCX)
    change_type: ChangeType
    expected_text: str
    actual_text: str
    internal_changes: list[str]
    severity: Severity | None = None
    severity_reasoning: str | None = None


@dataclass
class SemanticResult:
    matches: bool
    details: str
    discrepancies: list[SemanticDiscrepancy] = field(default_factory=list)


@dataclass
class VisualVerdict:
    available: bool
    status: str | None = None  # "PASSED" | "FAILED"
    findings: str | None = None
    error: str | None = None


@dataclass
class ComparisonSummary:
    status: str  # "PASSED" | "FAILED"
    total_discrepancies: int
    critical: int
    warning: int
    info: int
    generated_at: datetime


@dataclass
class ComparisonResult:
    actual_path: str
    expected_path: str
    structural: StructuralResult
    semantic: SemanticResult
    visual: VisualVerdict | None  # None si enable_visual=False
    summary: ComparisonSummary
