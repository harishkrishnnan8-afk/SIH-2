from backend.app.core.masking import hash_apaar, mask_apaar, sanitize_csv_cell
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.rules.engine import validate_student_record


def test_apaar_masking():
    # Revealing only last 4 digits
    assert mask_apaar("123456789012") == "•••• •••• 9012"
    assert mask_apaar("1234") == "•••• •••• 1234"
    assert mask_apaar("123") == "•••• •••• ••••"
    assert mask_apaar("") == "•••• •••• ••••"


def test_csv_formula_injection_sanitization():
    # CWE-1236 mitigation
    assert sanitize_csv_cell("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("-12345") == "'-12345"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("Normal Text") == "Normal Text"
    assert sanitize_csv_cell(None) == ""


def test_rule_r_fmt_02_invalid_apaar(db):
    findings = validate_student_record(
        db=db,
        institution_id="INS-001",
        name="Test Student",
        raw_apaar="12345",  # Not 12 digits
        programme_code="BT-CSE",
        admission_category="General",
    )
    rule_codes = [f["rule_code"] for f in findings]
    assert "R-FMT-02" in rule_codes


def test_rule_r_req_01_missing_name(db):
    findings = validate_student_record(
        db=db,
        institution_id="INS-001",
        name="",
        raw_apaar="123456789012",
        programme_code="BT-CSE",
        admission_category="General",
    )
    rule_codes = [f["rule_code"] for f in findings]
    assert "R-REQ-01" in rule_codes


def test_rule_r_cat_01_invalid_category(db):
    findings = validate_student_record(
        db=db,
        institution_id="INS-001",
        name="Test Student",
        raw_apaar="123456789012",
        programme_code="BT-CSE",
        admission_category="InvalidCategory",
    )
    rule_codes = [f["rule_code"] for f in findings]
    assert "R-CAT-01" in rule_codes


def test_rule_r_dup_01_same_name_and_dob(db):
    # Add existing student
    stu = Student(
        id="STU-EXIST-1",
        institution_id="INS-001",
        name="Aarav Sharma",
        dob="2005-04-12",
        gender="Male",
        masked_apaar="•••• •••• 1111",
        apaar_hash=hash_apaar("999999991111"),
        status="Verified",
    )
    db.add(stu)
    db.commit()

    # Validate new student with same name and dob
    findings = validate_student_record(
        db=db,
        institution_id="INS-001",
        name="Aarav Sharma",
        raw_apaar="888888882222",
        programme_code="BT-CSE",
        admission_category="General",
        dob="2005-04-12",
    )
    rule_codes = [f["rule_code"] for f in findings]
    assert "R-DUP-01" in rule_codes


def test_rule_r_cross_01_cross_institution_match(db):
    # Student in INS-002
    stu2 = Student(
        id="STU-INS2-1",
        institution_id="INS-002",
        name="Other Student",
        dob="2006-01-01",
        gender="Female",
        masked_apaar="•••• •••• 7777",
        apaar_hash=hash_apaar("123456787777"),
        status="Verified",
    )
    db.add(stu2)
    db.commit()

    # Validate in INS-001 with same APAAR
    findings = validate_student_record(
        db=db,
        institution_id="INS-001",
        name="New Student",
        raw_apaar="123456787777",
        programme_code="BT-CSE",
        admission_category="General",
    )
    rule_codes = [f["rule_code"] for f in findings]
    assert "R-CROSS-01" in rule_codes


def test_rule_r_int_01_intake_exceeded(db):
    prog = db.query(Programme).filter(Programme.institution_id == "INS-001", Programme.code == "BT-CSE").first()
    # approved intake is 2 in conftest
    # Add 2 admitted students
    for i in range(2):
        s = Student(
            id=f"STU-INT-{i}",
            institution_id="INS-001",
            name=f"Student {i}",
            dob="2005-01-01",
            gender="Male",
            masked_apaar=f"•••• •••• {i:04d}",
            apaar_hash=hash_apaar(f"99990000{i:04d}"),
            status="Verified",
        )
        db.add(s)
        db.flush()
        adm = Admission(
            student_id=s.id,
            programme_id=prog.id,
            institution_id="INS-001",
            academic_year="2026–27",
            admission_year=2026,
            category="General",
            admission_status="Admitted",
        )
        db.add(adm)
    db.commit()

    # Third student should trigger R-INT-01
    findings = validate_student_record(
        db=db,
        institution_id="INS-001",
        name="Third Student",
        raw_apaar="999900009999",
        programme_code="BT-CSE",
        admission_category="General",
    )
    rule_codes = [f["rule_code"] for f in findings]
    assert "R-INT-01" in rule_codes
