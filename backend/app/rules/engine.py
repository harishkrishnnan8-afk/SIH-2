import random
import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.masking import hash_apaar, mask_apaar
from backend.app.models.admission import Admission
from backend.app.models.finding import ValidationFinding
from backend.app.models.intake import IntakeConfig
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.rules.definitions import RULES, RuleDefinition

VALID_CATEGORIES = {"General", "Supernumerary", "NRI", "OCI", "Foreign National"}


def generate_finding_id(db: Session) -> str:
    """Generate a clean finding ID like FND-2601."""
    for _ in range(100):
        rnd = random.randint(2600, 9999)
        fid = f"FND-{rnd}"
        if not db.query(ValidationFinding).filter(ValidationFinding.id == fid).first():
            return fid
    return f"FND-{random.randint(10000, 99999)}"


def validate_student_record(
    db: Session,
    institution_id: str,
    name: str,
    raw_apaar: str,
    programme_code: str,
    admission_category: str,
    dob: str = "2006-01-01",
    is_oci: bool = False,
    oci_card_number: Optional[str] = None,
    existing_student_id: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Deterministic rule validation for a student admission record.
    Returns list of finding dictionaries.
    """
    findings = []
    digits = re.sub(r"\D", "", raw_apaar or "")
    apaar_h = hash_apaar(digits) if digits else ""

    # 1. Required name check
    if not name or len(name.strip()) < 2:
        rule = RULES["R-REQ-01"]
        findings.append({
            "rule_code": rule.code,
            "category": rule.category,
            "severity": rule.severity,
            "rule": f"{rule.code}: {rule.message}",
            "evidence": "Student name field is empty or under 2 characters.",
            "next_steps": rule.next_steps,
        })

    # 2. APAAR format check (exactly 12 digits)
    if len(digits) != 12:
        rule = RULES["R-FMT-02"]
        findings.append({
            "rule_code": rule.code,
            "category": rule.category,
            "severity": rule.severity,
            "rule": f"{rule.code}: {rule.message}",
            "evidence": f"Submitted identifier '{mask_apaar(digits)}' has {len(digits)} digits; expected 12.",
            "next_steps": rule.next_steps,
        })

    # 3. Programme code validation
    programme = (
        db.query(Programme)
        .filter(
            Programme.institution_id == institution_id,
            Programme.code == programme_code,
        )
        .first()
    )
    if not programme:
        rule = RULES["R-REQ-02"]
        findings.append({
            "rule_code": rule.code,
            "category": rule.category,
            "severity": rule.severity,
            "rule": f"{rule.code}: {rule.message}",
            "evidence": f"Programme code '{programme_code}' does not exist for institution {institution_id}.",
            "next_steps": rule.next_steps,
        })

    # 4. Admission category check
    if not admission_category or admission_category.strip() == "":
        rule = RULES["R-REQ-04"]
        findings.append({
            "rule_code": rule.code,
            "category": rule.category,
            "severity": rule.severity,
            "rule": f"{rule.code}: {rule.message}",
            "evidence": "Admission category was not specified.",
            "next_steps": rule.next_steps,
        })
    elif admission_category not in VALID_CATEGORIES:
        rule = RULES["R-CAT-01"]
        findings.append({
            "rule_code": rule.code,
            "category": rule.category,
            "severity": rule.severity,
            "rule": f"{rule.code}: {rule.message}",
            "evidence": f"'{admission_category}' is not an approved category.",
            "next_steps": rule.next_steps,
        })

    # 5. OCI confirmation check
    if admission_category == "OCI" and not is_oci and not oci_card_number:
        rule = RULES["R-CAT-03"]
        findings.append({
            "rule_code": rule.code,
            "category": rule.category,
            "severity": rule.severity,
            "rule": f"{rule.code}: {rule.message}",
            "evidence": "Record is marked OCI category but OCI card confirmation is missing.",
            "next_steps": rule.next_steps,
        })

    # 6. Within-institution duplicate detection by APAAR hash
    if len(digits) == 12:
        dup_query = db.query(Student).filter(
            Student.institution_id == institution_id,
            Student.apaar_hash == apaar_h,
        )
        if existing_student_id:
            dup_query = dup_query.filter(Student.id != existing_student_id)
        existing_dup = dup_query.first()
        if existing_dup:
            rule = RULES["R-DUP-02"]
            findings.append({
                "rule_code": rule.code,
                "category": rule.category,
                "severity": rule.severity,
                "rule": f"{rule.code}: {rule.message}",
                "evidence": f"Identifier matches existing active student record {existing_dup.id} ({existing_dup.name}).",
                "next_steps": rule.next_steps,
            })

        # 7. Cross-institution duplicate check
        cross_dup = (
            db.query(Student)
            .filter(
                Student.institution_id != institution_id,
                Student.apaar_hash == apaar_h,
            )
            .first()
        )
        if cross_dup:
            rule = RULES["R-CROSS-01"]
            findings.append({
                "rule_code": rule.code,
                "category": rule.category,
                "severity": rule.severity,
                "rule": f"{rule.code}: {rule.message}",
                "evidence": f"APAAR identifier matches an existing record in institution {cross_dup.institution_id}.",
                "next_steps": rule.next_steps,
            })

    # 8. Within-institution duplicate by Name + DOB
    if name and dob:
        name_dob_query = db.query(Student).filter(
            Student.institution_id == institution_id,
            Student.name.ilike(name.strip()),
            Student.dob == dob,
        )
        if existing_student_id:
            name_dob_query = name_dob_query.filter(Student.id != existing_student_id)
        if name_dob_query.first():
            rule = RULES["R-DUP-01"]
            findings.append({
                "rule_code": rule.code,
                "category": rule.category,
                "severity": rule.severity,
                "rule": f"{rule.code}: {rule.message}",
                "evidence": f"Name '{name.strip()}' and DOB '{dob}' match another record in this institution.",
                "next_steps": rule.next_steps,
            })

    # 9. Programme Intake Capacity Check
    if programme:
        # Check intake configuration policy for supernumerary exclusions
        intake_cfg = (
            db.query(IntakeConfig)
            .filter(
                IntakeConfig.institution_id == institution_id,
                IntakeConfig.academic_year == programme.academic_year,
            )
            .first()
        )
        exclude_supernumerary = intake_cfg.supernumerary_excluded if intake_cfg else True

        admissions_q = db.query(Admission).filter(
            Admission.programme_id == programme.id,
            Admission.admission_status == "Admitted",
        )
        if exclude_supernumerary:
            admissions_q = admissions_q.filter(Admission.category != "Supernumerary")

        current_count = admissions_q.count()
        # If adding one more would exceed approved intake
        is_counting = admission_category != "Supernumerary" if exclude_supernumerary else True
        if is_counting and (current_count + 1) > programme.approved_intake:
            rule = RULES["R-INT-01"]
            findings.append({
                "rule_code": rule.code,
                "category": rule.category,
                "severity": rule.severity,
                "rule": f"{rule.code}: {rule.message}",
                "evidence": f"Programme {programme.code} has {current_count} enrolled against approved intake of {programme.approved_intake}.",
                "next_steps": rule.next_steps,
            })

    return findings


def persist_findings(
    db: Session,
    institution_id: str,
    findings_data: List[Dict[str, str]],
    student_id: Optional[str] = None,
) -> List[ValidationFinding]:
    """Persist validation findings into database."""
    created = []
    for f in findings_data:
        fid = generate_finding_id(db)
        finding = ValidationFinding(
            id=fid,
            institution_id=institution_id,
            student_id=student_id,
            category=f["category"],
            severity=f["severity"],
            rule=f["rule"],
            evidence=f["evidence"],
            next_steps=f["next_steps"],
            status="Open",
        )
        db.add(finding)
        created.append(finding)
    db.flush()
    return created
