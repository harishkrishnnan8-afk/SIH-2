from pydantic import BaseModel, ConfigDict


class ProgrammeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    year: str
    approvedIntake: int
    actualEnrolment: int
    institutionId: str
    policy: str


class ProgrammeCreate(BaseModel):
    code: str
    name: str
    year: str = "2026–27"
    approvedIntake: int = 60
    policy: str = "Supernumerary excluded"
