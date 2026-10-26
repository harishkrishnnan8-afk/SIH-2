import csv
import io
import random
import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.audit import log_audit_event
from backend.app.core.masking import hash_apaar, mask_apaar, sanitize_csv_cell
from backend.app.models.admission import Admission
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.upload import UploadBatch, UploadRowResult
from backend.app.models.user import User
from backend.app.rules.definitions import RULES
from backend.app.rules.engine import persist_findings, validate_student_record

TEMPLATE_HEADERS = [
    "student_name",
    "apaar_id",
    "programme_code",
    "academic_year",
    "admission_category",
    "admission_status",
    "date_of_birth",
]

CATEGORIES = ["General", "Supernumerary", "NRI", "OCI", "Foreign National"]


def generate_batch_id(db: Session) -> str:
    for _ in range(100):
        rnd = random.randint(100, 9999)
        bid = f"BATCH-{rnd:04d}"
        if not db.query(UploadBatch).filter(UploadBatch.id == bid).first():
            return bid
    return f"BATCH-{random.randint(10000, 99999)}"


def process_csv_upload(
    db: Session,
    file_bytes: bytes,
    filename: str,
    institution_id: str,
    current_user: User,
) -> Tuple[UploadBatch, List[Dict[str, object]]]:
    """
    Robust CSV ingestion pipeline.
    Validates headers, rows, detects duplicates, persists batch,
    persists accepted records, and stores row-level errors.
    """
    # 1. Decode UTF-8 safely
    try:
        content = file_bytes.decode("utf-8-sig")  # handles potential BOM
    except UnicodeDecodeError:
        raise ValueError("File encoding is not valid UTF-8.")

    # 2. Parse CSV
    reader = csv.reader(io.StringIO(content))
    rows = [r for r in reader if any(cell.strip() for cell in r)]
    if len(rows) < 2:
        raise ValueError("The CSV file is empty or contains only a header row.")

    header_row = [h.strip().lower() for h in rows[0]]
    data_rows = rows[1:]

    # 3. Check for required header mappings
    header_mapping = {}
    for req in ["student_name", "apaar_id", "programme_code"]:
        matched_idx = -1
        for idx, col in enumerate(header_row):
            if col == req:
                matched_idx = idx
                break
        if matched_idx == -1:
            raise ValueError(f"Missing required CSV column header: '{req}'.")
        header_mapping[req] = matched_idx

    # Optional column mappings
    for opt in ["academic_year", "admission_category", "admission_status", "date_of_birth"]:
        header_mapping[opt] = header_row.index(opt) if opt in header_row else -1

    batch_id = generate_batch_id(db)
    batch = UploadBatch(
        id=batch_id,
        institution_id=institution_id,
        filename=filename,
        uploaded_by_name=current_user.full_name,
        uploaded_by_user_id=current_user.id,
        status="Processing",
        total=len(data_rows),
        accepted=0,
        rejected=0,
    )
    db.add(batch)
    db.flush()

    row_errors = []
    seen_in_batch = set()
    accepted_count = 0
    rejected_count = 0

    # Cache programmes for this institution
    programmes = {
        p.code: p for p in db.query(Programme).filter(Programme.institution_id == institution_id).all()
    }

    for idx, r in enumerate(data_rows):
        row_num = idx + 2  # 1-indexed, header is row 1
        
        def val(col_name: str) -> str:
            col_idx = header_mapping.get(col_name, -1)
            if 0 <= col_idx < len(r):
                return r[col_idx].strip()
            return ""

        name = val("student_name")
        raw_apaar = val("apaar_id")
        prog_code = val("programme_code")
        acad_year = val("academic_year") or "2026–27"
        cat = val("admission_category") or "General"
        dob = val("date_of_birth") or "2006-01-01"
        adm_status = val("admission_status") or "Admitted"

        row_failed = False

        # Name check
        if not name:
            row_errors.append({
                "row": row_num,
                "field": "student_name",
                "value": "",
                "rule": "Student name is required.",
            })
            row_failed = True

        # APAAR 12-digit format check
        clean_apaar = re.sub(r"\D", "", raw_apaar)
        if len(clean_apaar) != 12:
            row_errors.append({
                "row": row_num,
                "field": "apaar_id",
                "value": mask_apaar(clean_apaar) if clean_apaar else "",
                "rule": "APAAR identifier must be exactly 12 digits.",
            })
            row_failed = True
        elif clean_apaar in seen_in_batch:
            row_errors.append({
                "row": row_num,
                "field": "apaar_id",
                "value": mask_apaar(clean_apaar),
                "rule": "Identifier repeated within this file.",
            })
            row_failed = True
        else:
            seen_in_batch.add(clean_apaar)

        # Programme code check
        if not prog_code:
            row_errors.append({
                "row": row_num,
                "field": "programme_code",
                "value": "",
                "rule": "Programme code is required.",
            })
            row_failed = True
        elif prog_code not in programmes:
            row_errors.append({
                "row": row_num,
                "field": "programme_code",
                "value": prog_code,
                "rule": f"Programme '{prog_code}' does not exist for this institution.",
            })
            row_failed = True

        # Category check
        if cat and cat not in CATEGORIES:
            row_errors.append({
                "row": row_num,
                "field": "admission_category",
                "value": cat,
                "rule": f"Category must be one of: {', '.join(CATEGORIES)}.",
            })
            row_failed = True

        if row_failed:
            rejected_count += 1
            continue

        # If row passed basic structural validation, check deeper rule engine
        findings = validate_student_record(
            db=db,
            institution_id=institution_id,
            name=name,
            raw_apaar=clean_apaar,
            programme_code=prog_code,
            admission_category=cat,
            dob=dob,
        )

        prog_obj = programmes[prog_code]
        student_status = "Pending review" if findings else "Verified"

        # Persist student & admission
        rnd_stu_id = f"STU-{random.randint(1001, 99999)}"
        new_stu = Student(
            id=rnd_stu_id,
            institution_id=institution_id,
            name=name,
            dob=dob,
            gender="Not specified",
            email=f"{name.split()[0].lower()}.{rnd_stu_id.lower()}@example.edu",
            masked_apaar=mask_apaar(clean_apaar),
            apaar_hash=hash_apaar(clean_apaar),
            status=student_status,
        )
        db.add(new_stu)
        db.flush()

        # Parse admission year
        adm_year_int = 2026
        m = re.search(r"(\d{4})", acad_year)
        if m:
            adm_year_int = int(m.group(1))

        new_adm = Admission(
            student_id=new_stu.id,
            programme_id=prog_obj.id,
            institution_id=institution_id,
            academic_year=acad_year,
            admission_year=adm_year_int,
            category=cat,
            admission_status=adm_status,
        )
        db.add(new_adm)

        if findings:
            persist_findings(
                db=db,
                institution_id=institution_id,
                findings_data=findings,
                student_id=new_stu.id,
            )

        accepted_count += 1

    # Persist row error records in database
    for err in row_errors:
        db_err = UploadRowResult(
            batch_id=batch.id,
            row_number=err["row"],
            field=err["field"],
            raw_value=sanitize_csv_cell(err["value"]),
            rule=err["rule"],
            is_error=True,
        )
        db.add(db_err)

    batch.total = len(data_rows)
    batch.accepted = accepted_count
    batch.rejected = rejected_count
    if rejected_count == 0:
        batch.status = "Completed"
    elif accepted_count > 0:
        batch.status = "Completed with errors"
    else:
        batch.status = "Failed"

    log_audit_event(
        db=db,
        action="Uploaded CSV batch",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=institution_id,
        ref=batch.id,
        result="Success" if batch.status != "Failed" else "Failed",
        details=f"Processed file '{filename}'. Accepted: {accepted_count}, Rejected: {rejected_count}.",
    )

    db.commit()
    db.refresh(batch)

    return batch, row_errors
