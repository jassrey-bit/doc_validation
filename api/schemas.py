from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.models import ChangeKind, ChangeType, DiscoveryMethod, Severity


class InternalChangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: ChangeKind
    description: str


class StructuralResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expected_sections: list[str]
    found_sections: list[str]
    missing_sections: list[str]
    score: float
    discovery_method: DiscoveryMethod


class SemanticDiscrepancyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location: int | str
    change_type: ChangeType
    expected_text: str
    actual_text: str
    internal_changes: list[InternalChangeOut]
    severity: Severity | None = None
    severity_reasoning: str | None = None


class SemanticResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    matches: bool
    details: str
    discrepancies: list[SemanticDiscrepancyOut]


class VisualVerdictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    available: bool
    status: str | None = None
    findings: str | None = None
    error: str | None = None


class ComparisonSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    total_discrepancies: int
    critical: int
    warning: int
    info: int
    generated_at: datetime


class ComparisonResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    actual_path: str
    expected_path: str
    structural: StructuralResultOut
    semantic: SemanticResultOut
    visual: VisualVerdictOut | None
    summary: ComparisonSummaryOut
