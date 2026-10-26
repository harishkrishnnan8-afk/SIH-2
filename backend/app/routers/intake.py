from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.permissions import Permission
from backend.app.database import get_db
from backend.app.models.intake import IntakeConfig
from backend.app.models.user import User
from backend.app.schemas.intake import IntakeConfigResponse, IntakeConfigUpdate

router = APIRouter(prefix="/intake-configuration", tags=["Intake Configuration"])


@router.get("", response_model=IntakeConfigResponse)
def get_intake_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_inst = current_user.institution_id or "INS-001"
    config = (
        db.query(IntakeConfig)
        .filter(IntakeConfig.institution_id == target_inst)
        .first()
    )
    if not config:
        # Default configuration
        config = IntakeConfig(
            institution_id=target_inst,
            academic_year="2026–27",
            supernumerary_excluded=True,
            nri_counted_separately=False,
            oci_special_quota=False,
            warn_threshold_pct=95,
            max_overrun_allowed=0,
        )
        db.add(config)
        db.commit()
        db.refresh(config)

    return config


@router.put("", response_model=IntakeConfigResponse)
def update_intake_config(
    payload: IntakeConfigUpdate,
    current_user: User = Depends(require_permission(Permission.CONFIGURE_INTAKE)),
    db: Session = Depends(get_db),
):
    target_inst = current_user.institution_id or "INS-001"
    config = (
        db.query(IntakeConfig)
        .filter(IntakeConfig.institution_id == target_inst)
        .first()
    )
    if not config:
        config = IntakeConfig(
            institution_id=target_inst,
            academic_year="2026–27",
        )
        db.add(config)

    config.supernumerary_excluded = payload.supernumerary_excluded
    config.nri_counted_separately = payload.nri_counted_separately
    config.oci_special_quota = payload.oci_special_quota
    config.warn_threshold_pct = payload.warn_threshold_pct
    config.max_overrun_allowed = payload.max_overrun_allowed

    log_audit_event(
        db=db,
        action="Changed intake configuration",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=target_inst,
        ref="CFG-INTAKE",
        result="Success",
        details="Updated supernumerary, NRI, and threshold intake rules",
    )
    db.commit()
    db.refresh(config)

    return config
