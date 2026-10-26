from typing import Optional
from pydantic import BaseModel, ConfigDict


class InstitutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    ref: str
    status: str
    state: str


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = None
