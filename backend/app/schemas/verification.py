from typing import Optional
from pydantic import BaseModel
from backend.app.schemas.student import StudentResponse


class VerificationRequest(BaseModel):
    id: str  # The input APAAR identifier to verify


class VerificationResponseSchema(BaseModel):
    mode: str
    formatValid: bool
    internalMatch: bool
    providerStatus: str
    checkedAt: str
    student: Optional[StudentResponse] = None
    isSimulated: bool = True
    simulationLabel: str = "SIMULATED — NOT OFFICIAL APAAR VERIFICATION"
