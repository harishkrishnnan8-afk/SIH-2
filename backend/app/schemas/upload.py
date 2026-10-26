from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ImportBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file: str
    uploadedBy: str
    at: str
    total: int
    accepted: int
    rejected: int
    status: str


class RowErrorResponse(BaseModel):
    row: int
    field: str
    value: str
    rule: str


class CsvValidationResult(BaseModel):
    accepted: int
    rejected: int
    total: int
    errors: List[RowErrorResponse]
    batch_id: Optional[str] = None
    persisted: bool = False
