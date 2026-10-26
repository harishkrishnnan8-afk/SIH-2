from typing import List, Dict, Any
from pydantic import BaseModel


class MetricCard(BaseModel):
    label: str
    value: int | str
    note: str
    tone: str | None = None


class CentralInstitutionSummary(BaseModel):
    id: str
    name: str
    ref: str
    status: str
    state: str
    enrolment: int
    intake: int
    findings: int
    submission: str
    quality: int


class CentralDashboardResponse(BaseModel):
    institutionsInScope: int
    totalEnrolment: int
    intakeUtilisationPct: int
    outstandingFindings: int
    institutions: List[CentralInstitutionSummary]
