from backend.app.core.masking import hash_apaar
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.student import Student


def test_cross_institution_student_access_is_forbidden(client, token_admin_ins1, token_admin_ins2, db):
    """
    SECURITY TEST:
    Verify that an authenticated admin from INS-001 CANNOT access student records
    belonging to INS-002, even if they guess or modify the student ID.
    Expected: HTTP 403 Forbidden.
    """
    prog2 = db.query(Programme).filter(Programme.institution_id == "INS-002").first()
    
    # Create student belonging to INS-002
    secret_student = Student(
        id="STU-SECRET-002",
        institution_id="INS-002",
        name="Confidential Student",
        dob="2005-02-02",
        gender="Female",
        masked_apaar="•••• •••• 8888",
        apaar_hash=hash_apaar("987654328888"),
        status="Verified",
    )
    db.add(secret_student)
    db.flush()

    adm2 = Admission(
        student_id=secret_student.id,
        programme_id=prog2.id,
        institution_id="INS-002",
        academic_year="2026–27",
        admission_year=2026,
        category="General",
        admission_status="Admitted",
    )
    db.add(adm2)
    db.commit()

    # 1. Admin from INS-002 CAN access their own student
    res_allowed = client.get(
        f"/api/v1/students/{secret_student.id}",
        headers={"Authorization": f"Bearer {token_admin_ins2}"},
    )
    assert res_allowed.status_code == 200
    assert res_allowed.json()["id"] == secret_student.id

    # 2. Admin from INS-001 attempts to access the INS-002 student -> MUST BE 403 FORBIDDEN
    res_forbidden = client.get(
        f"/api/v1/students/{secret_student.id}",
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res_forbidden.status_code == 403
    assert "Forbidden" in res_forbidden.json()["detail"]


def test_student_list_filters_by_institution_automatically(client, token_admin_ins1, token_admin_ins2, db):
    """
    SECURITY TEST:
    Verify that GET /api/v1/students returns ONLY records for the user's institution.
    """
    res1 = client.get("/api/v1/students", headers={"Authorization": f"Bearer {token_admin_ins1}"})
    assert res1.status_code == 200
    for s in res1.json():
        assert s["institutionId"] == "INS-001"

    res2 = client.get("/api/v1/students", headers={"Authorization": f"Bearer {token_admin_ins2}"})
    assert res2.status_code == 200
    for s in res2.json():
        assert s["institutionId"] == "INS-002"


def test_unauthenticated_request_is_denied(client):
    """
    SECURITY TEST:
    Verify deny-by-default on protected student endpoints when unauthenticated.
    """
    res = client.get("/api/v1/students")
    assert res.status_code == 401
