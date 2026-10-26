import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user
from backend.app.core.masking import hash_apaar, mask_apaar
from backend.app.database import get_db
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.models.verification import VerificationAttempt
from backend.app.schemas.student import StudentResponse
from backend.app.schemas.verification import VerificationRequest, VerificationResponseSchema
from backend.app.verification.mock_provider import get_verification_provider

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.post("/verify", response_model=VerificationResponseSchema)
def verify_apaar_identifier(
    payload: VerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clean_digits = re.sub(r"\D", "", payload.id or "")
    masked = mask_apaar(clean_digits)
    apaar_h = hash_apaar(clean_digits) if len(clean_digits) == 12 else ""

    # Look up in internal institution records
    matched_student = None
    if apaar_h:
        matched_student = (
            db.query(Student)
            .filter(
                Student.institution_id == current_user.institution_id,
                Student.apaar_hash == apaar_h,
            )
            .first()
        )

    # Invoke verification provider adapter
    provider = get_verification_provider()
    resp = provider.verify(clean_digits, internal_student=matched_student)

    # Persist verification attempt
    attempt = VerificationAttempt(
        institution_id=current_user.institution_id,
        user_id=current_user.id,
        apaar_query_masked=masked,
        mode=resp.mode,
        format_valid=resp.format_valid,
        internal_match=resp.internal_match,
        matched_student_id=matched_student.id if matched_student else None,
        provider_status=resp.provider_status,
        is_simulated=resp.is_simulated,
        simulation_label=resp.simulation_label,
        raw_response_summary=resp.message,
    )
    db.add(attempt)

    # Record audit event
    log_audit_event(
        db=db,
        action="Verification attempt",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=current_user.institution_id,
        ref=masked,
        result="Success" if resp.format_valid else "Failed",
        details=f"Provider: {resp.provider_status} ({resp.simulation_label})",
    )
    db.commit()

    student_res = None
    if matched_student:
        adm = db.query(Admission).filter(Admission.student_id == matched_student.id).first()
        prog = db.query(Programme).filter(Programme.id == adm.programme_id).first() if adm else None
        student_res = StudentResponse(
            id=matched_student.id,
            name=matched_student.name,
            apaar=matched_student.masked_apaar,
            programme=prog.code if prog else "N/A",
            admissionYear=adm.admission_year if adm else 2026,
            category=adm.category if adm else "General",
            status=matched_student.status,
            updated=matched_student.updated_at.isoformat(),
            dob=matched_student.dob,
            gender=matched_student.gender,
            email=matched_student.email or "",
            institutionId=matched_student.institution_id,
        )

    return VerificationResponseSchema(
        mode=resp.mode,
        formatValid=resp.format_valid,
        internalMatch=resp.internal_match,
        providerStatus=resp.provider_status,
        checkedAt=resp.checked_at,
        student=student_res,
        isSimulated=resp.is_simulated,
        simulationLabel=resp.simulation_label,
    )
