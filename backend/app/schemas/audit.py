from pydantic import BaseModel, ConfigDict


class AuditEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    at: str
    actor: str
    role: str
    action: str
    ref: str
    result: str
