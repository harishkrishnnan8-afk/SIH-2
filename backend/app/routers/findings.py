from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.permissions import Permission, Role, require_institution_access
from backend.app.database import get_db
from backend.app.models.finding import ValidationFinding
from backend.app.models.review import ReviewAction
from backend.app.models.user import User
from backend.app.schemas.finding import FindingActionRequest, FindingResponse

router = APIRouter(prefix="/findings", tags=["Validation Findings"])


@router.get("", response_model=List[FindingResponse])
def list_findings(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ValidationFinding)
    if current_user.role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        query = query.filter(ValidationFinding.institution_id == current_user.institution_id)

    if status_filter and status_filter != "all":
        query = query.filter(ValidationFinding.status == status_filter)

    findings = query.order_by(ValidationFinding.detected_at.desc()).all()

    return [
        FindingResponse(
            id=f.id,
            studentId=f.student_id,
            category=f.category,
            severity=f.severity,
            detected=f.detected_at.isoformat(),
            status=f.status,
            reviewer=f.reviewer_name,
            rule=f.rule,
            evidence=f.evidence,
            nextSteps=f.next_steps,
        )
        for f in findings
    ]


@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding = db.query(ValidationFinding).filter(ValidationFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding '{finding_id}' not found.",
        )

    require_institution_access(current_user, finding.institution_id)

    return FindingResponse(
        id=finding.id,
        studentId=finding.student_id,
        category=finding.category,
        severity=finding.severity,
        detected=finding.detected_at.isoformat(),
        status=finding.status,
        reviewer=finding.reviewer_name,
        rule=finding.rule,
        evidence=finding.evidence,
        nextSteps=finding.next_steps,
    )


@router.post("/{finding_id}/actions", response_model=FindingResponse)
def apply_review_action(
    finding_id: str,
    payload: FindingActionRequest,
    current_user: User = Depends(require_permission(Permission.REVIEW_FINDING)),
    db: Session = Depends(get_db),
):
    finding = db.query(ValidationFinding).filter(ValidationFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding '{finding_id}' not found.",
        )

    require_institution_access(current_user, finding.institution_id)

    action_map = {
        "Start review": "Under review",
        "Request correction": "Under review",
        "Escalate": "Escalated",
        "Resolve": "Resolved",
    }
    new_status = action_map.get(payload.action, finding.status)
    prev_status = finding.status

    finding.status = new_status
    finding.reviewer_name = current_user.full_name
    if new_status == "Resolved":
        finding.resolved_at = datetime.now(timezone.utc)

    # Persist review action
    review_action = ReviewAction(
        finding_id=finding.id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action=payload.action,
        previous_status=prev_status,
        new_status=new_status,
        note=payload.note,
    )
    db.add(review_action)

    # Log audit event
    audit_action = f"{payload.action} finding"
    log_audit_event(
        db=db,
        action=audit_action,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=finding.institution_id,
        ref=finding.id,
        result="Success",
        details=f"Status changed from {prev_status} to {new_status}. Note: {payload.note or 'None'}",
    )

    db.commit()
    db.refresh(finding)

    return FindingResponse(
        id=finding.id,
        studentId=finding.student_id,
        category=finding.category,
        severity=finding.severity,
        detected=finding.detected_at.isoformat(),
        status=finding.status,
        reviewer=finding.reviewer_name,
        rule=finding.rule,
        evidence=finding.evidence,
        nextSteps=finding.next_steps,
    )
