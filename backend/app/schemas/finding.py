from typing import Optional
from pydantic import BaseModel, ConfigDict


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    studentId: Optional[str] = None
    category: str
    severity: str
    detected: str
    status: str
    reviewer: Optional[str] = None
    rule: str
    evidence: str
    nextSteps: str


class FindingActionRequest(BaseModel):
    action: str  # "Start review", "Request correction", "Escalate", "Resolve"
    note: Optional[str] = ""
