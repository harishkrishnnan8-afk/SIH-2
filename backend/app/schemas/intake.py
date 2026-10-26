from pydantic import BaseModel, ConfigDict


class IntakeConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    institution_id: str
    academic_year: str
    supernumerary_excluded: bool
    nri_counted_separately: bool
    oci_special_quota: bool
    warn_threshold_pct: int
    max_overrun_allowed: int


class IntakeConfigUpdate(BaseModel):
    supernumerary_excluded: bool
    nri_counted_separately: bool
    oci_special_quota: bool
    warn_threshold_pct: int = 95
    max_overrun_allowed: int = 0
