from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    apaar: str = Field(..., description="12-digit APAAR identifier")
    programme: str = Field(..., description="Programme code, e.g. BT-CSE")
    year: str = Field("2026–27", description="Academic year")
    category: str = Field("General", description="General, Supernumerary, NRI, OCI, Foreign National")
    status: str = Field("Admitted", description="Admission status")
    nri: bool = False
    oci: bool = False
    ociCard: Optional[str] = None
    foreign: bool = False
    nationality: Optional[str] = None
    dob: Optional[str] = "2006-01-01"
    gender: Optional[str] = "Not specified"
    email: Optional[str] = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    apaar: str  # Masked APAAR for safe display (•••• •••• 9012)
    programme: str
    admissionYear: int
    category: str
    status: str
    updated: str
    dob: str
    gender: str
    email: str
    institutionId: str


class SaveStudentResult(BaseModel):
    persisted: bool
    student_id: Optional[str] = None
    findings_count: int = 0
    message: str
