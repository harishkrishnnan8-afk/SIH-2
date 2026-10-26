"""
DEMO ENVIRONMENT — SYNTHETIC DATA
Repeatable seed process using fictional institutions, programmes, students, and admissions.
Never use real student personal data or present synthetic identifiers as authentic APAAR IDs.
"""

from datetime import datetime, timezone
import random
from sqlalchemy.orm import Session

from backend.app.core.masking import hash_apaar, mask_apaar
from backend.app.core.security import get_password_hash
from backend.app.database import SessionLocal, engine, Base
from backend.app.models.admission import Admission
from backend.app.models.audit import AuditEvent
from backend.app.models.finding import ValidationFinding
from backend.app.models.institution import Institution
from backend.app.models.intake import IntakeConfig
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.upload import UploadBatch, UploadRowResult
from backend.app.models.user import User

DEMO_INSTITUTIONS = [
    {"id": "INS-001", "name": "Demo Institute of Technology, North Campus", "ref": "DEMO-AICTE-0001", "status": "Active", "state": "Delhi"},
    {"id": "INS-002", "name": "Sample College of Engineering", "ref": "DEMO-AICTE-0002", "status": "Active", "state": "Maharashtra"},
    {"id": "INS-003", "name": "Example School of Management", "ref": "DEMO-AICTE-0003", "status": "Under review", "state": "Karnataka"},
    {"id": "INS-004", "name": "Placeholder Polytechnic", "ref": "DEMO-AICTE-0004", "status": "Active", "state": "Tamil Nadu"},
    {"id": "INS-005", "name": "Synthetic University of Applied Sciences", "ref": "DEMO-AICTE-0005", "status": "Suspended", "state": "Gujarat"},
]

DEMO_PROGRAMMES = [
    {"code": "BT-CSE", "name": "B.Tech Computer Science & Engineering", "year": "2026–27", "approvedIntake": 180, "institutionId": "INS-001", "policy": "Supernumerary excluded"},
    {"code": "BT-ECE", "name": "B.Tech Electronics & Communication", "year": "2026–27", "approvedIntake": 120, "institutionId": "INS-001", "policy": "Supernumerary excluded"},
    {"code": "BT-ME", "name": "B.Tech Mechanical Engineering", "year": "2026–27", "approvedIntake": 120, "institutionId": "INS-001", "policy": "Pending confirmation"},
    {"code": "BT-CE", "name": "B.Tech Civil Engineering", "year": "2026–27", "approvedIntake": 60, "institutionId": "INS-001", "policy": "Supernumerary excluded"},
    {"code": "MBA", "name": "Master of Business Administration", "year": "2026–27", "approvedIntake": 120, "institutionId": "INS-001", "policy": "NRI counted separately"},
    {"code": "MCA", "name": "Master of Computer Applications", "year": "2026–27", "approvedIntake": 60, "institutionId": "INS-001", "policy": "Supernumerary excluded"},
    # INS-002 programmes for cross-tenant testing
    {"code": "BT-CSE", "name": "B.Tech Computer Science & Engineering", "year": "2026–27", "approvedIntake": 120, "institutionId": "INS-002", "policy": "Supernumerary excluded"},
]

DEMO_USERS = [
    {
        "id": "USR-001",
        "username": "priya.nair",
        "email": "priya.nair@example.edu",
        "password": "Password@123",
        "full_name": "Priya Nair",
        "role": "institution_admin",
        "institution_id": "INS-001",
    },
    {
        "id": "USR-002",
        "username": "k.rao",
        "email": "k.rao@example.edu",
        "password": "Password@123",
        "full_name": "K. Rao",
        "role": "institution_operator",
        "institution_id": "INS-001",
    },
    {
        "id": "USR-003",
        "username": "r.menon",
        "email": "r.menon@aicte.gov.in",
        "password": "Password@123",
        "full_name": "R. Menon",
        "role": "central_reviewer",
        "institution_id": None,
    },
    {
        "id": "USR-004",
        "username": "s.kulkarni",
        "email": "s.kulkarni@example.edu",
        "password": "Password@123",
        "full_name": "S. Kulkarni",
        "role": "authorized_verifier",
        "institution_id": "INS-001",
    },
    {
        "id": "USR-005",
        "username": "admin.ins002",
        "email": "admin@sample.edu",
        "password": "Password@123",
        "full_name": "Sample Admin",
        "role": "institution_admin",
        "institution_id": "INS-002",
    },
]

FIRST_NAMES = ["Aarav", "Ananya", "Vihaan", "Diya", "Arjun", "Isha", "Kabir", "Meera", "Rohan", "Saanvi", "Aditya", "Kavya", "Nikhil", "Priya", "Rahul", "Sneha", "Tanvi", "Yash", "Zoya", "Farhan"]
LAST_NAMES = ["Sharma", "Iyer", "Reddy", "Patel", "Nair", "Gupta", "Khan", "Das", "Menon", "Singh", "Joshi", "Bose", "Rao", "Mehta", "Pillai"]
CATEGORIES = ["General", "General", "General", "Supernumerary", "NRI", "OCI", "Foreign National"]
STATUSES = ["Verified", "Verified", "Pending review", "Pending review", "Flagged", "Draft"]


def seed_database():
    db: Session = SessionLocal()
    try:
        print("Initializing database tables...")
        Base.metadata.create_all(bind=engine)

        # Clear existing demo data
        db.query(AuditEvent).delete()
        db.query(UploadRowResult).delete()
        db.query(UploadBatch).delete()
        db.query(ValidationFinding).delete()
        db.query(Admission).delete()
        db.query(Student).delete()
        db.query(IntakeConfig).delete()
        db.query(Programme).delete()
        db.query(User).delete()
        db.query(Institution).delete()
        db.commit()

        print("Seeding institutions...")
        for inst_data in DEMO_INSTITUTIONS:
            inst = Institution(**inst_data)
            db.add(inst)
        db.commit()

        print("Seeding users...")
        for u_data in DEMO_USERS:
            user = User(
                id=u_data["id"],
                username=u_data["username"],
                email=u_data["email"],
                hashed_password=get_password_hash(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                institution_id=u_data["institution_id"],
            )
            db.add(user)
        db.commit()

        print("Seeding programmes and intake configs...")
        for p_data in DEMO_PROGRAMMES:
            p = Programme(
                code=p_data["code"],
                name=p_data["name"],
                academic_year=p_data["year"],
                approved_intake=p_data["approvedIntake"],
                institution_id=p_data["institutionId"],
                policy=p_data["policy"],
            )
            db.add(p)

        intake_cfg1 = IntakeConfig(
            institution_id="INS-001",
            academic_year="2026–27",
            supernumerary_excluded=True,
            nri_counted_separately=False,
            oci_special_quota=False,
            warn_threshold_pct=95,
            max_overrun_allowed=0,
        )
        db.add(intake_cfg1)
        db.commit()

        # Reload programmes map
        prog_map = {(p.institution_id, p.code): p for p in db.query(Programme).all()}

        print("Seeding synthetic students and admissions...")
        random.seed(26263)
        created_students = []

        for i in range(64):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            digits = str(100000000000 + random.randint(10000000000, 89999999999))
            masked = mask_apaar(digits)
            apaar_h = hash_apaar(digits)
            status = random.choice(STATUSES)
            dob = f"200{random.randint(4, 7)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            email = f"{first.lower()}.{1001 + i}@example.edu"
            
            stu = Student(
                id=f"STU-{1001 + i}",
                institution_id="INS-001",
                name=full_name,
                dob=dob,
                gender=random.choice(["Female", "Male"]),
                email=email,
                masked_apaar=masked,
                apaar_hash=apaar_h,
                status=status,
            )
            db.add(stu)
            db.flush()

            # Choose programme
            prog_code = random.choice(["BT-CSE", "BT-ECE", "BT-ME", "BT-CE", "MBA", "MCA"])
            prog_obj = prog_map[("INS-001", prog_code)]
            cat = random.choice(CATEGORIES)
            
            adm = Admission(
                student_id=stu.id,
                programme_id=prog_obj.id,
                institution_id="INS-001",
                academic_year="2026–27",
                admission_year=random.choice([2023, 2024, 2025, 2026]),
                category=cat,
                admission_status="Admitted",
            )
            db.add(adm)
            created_students.append(stu)

        # Cross-institution student test record in INS-002 with same APAAR hash to demonstrate R-CROSS-01
        cross_digits = "123456789012"
        cross_stu = Student(
            id="STU-9999",
            institution_id="INS-002",
            name="Vikram Seth",
            dob="2005-08-15",
            gender="Male",
            email="vikram@sample.edu",
            masked_apaar=mask_apaar(cross_digits),
            apaar_hash=hash_apaar(cross_digits),
            status="Verified",
        )
        db.add(cross_stu)
        db.flush()

        prog_ins2 = prog_map[("INS-002", "BT-CSE")]
        cross_adm = Admission(
            student_id=cross_stu.id,
            programme_id=prog_ins2.id,
            institution_id="INS-002",
            academic_year="2026–27",
            admission_year=2026,
            category="General",
            admission_status="Admitted",
        )
        db.add(cross_adm)
        db.commit()

        print("Seeding validation findings...")
        finding_types = [
            ("Possible duplicate", "R-DUP-01: Two records share the same name and date of birth within one institution.", "Name and date of birth match another active record in this programme.", "Compare both records with admission documents. A possible duplicate is not proof of fraud.", "High"),
            ("Identifier format", "R-FMT-02: APAAR identifier must contain exactly 12 digits.", "Submitted identifier failed the format check during import.", "Request a corrected identifier from the student or admissions office.", "Medium"),
            ("Intake exceeded", "R-INT-01: Enrolment in a programme exceeds the configured approved intake.", "Programme enrolment is above the configured approved intake value.", "Confirm whether supernumerary seats apply under the intake configuration.", "High"),
            ("Missing attribute", "R-REQ-04: Admission category is required for all admitted students.", "Admission category field was empty in the uploaded row.", "Update the admission record with the correct category.", "Medium"),
            ("Category mismatch", "R-CAT-03: OCI status must be confirmed for OCI category admissions.", "Record is marked OCI category but OCI status is not confirmed.", "Request a correction or attach confirmation.", "Medium"),
        ]

        f_statuses = ["Open", "Open", "Under review", "Resolved", "Escalated"]
        for i in range(28):
            ft = random.choice(finding_types)
            st = random.choice(f_statuses)
            stu = random.choice(created_students)
            reviewer = None if st == "Open" else random.choice(["R. Menon", "S. Kulkarni", "A. Verma"])
            
            finding = ValidationFinding(
                id=f"FND-{2601 + i}",
                institution_id="INS-001",
                student_id=stu.id,
                category=ft[0],
                severity=ft[4],
                rule=ft[1],
                evidence=ft[2],
                next_steps=ft[3],
                status=st,
                reviewer_name=reviewer,
            )
            db.add(finding)
        db.commit()

        print("Seeding upload batches...")
        demo_batches = [
            {"id": "BATCH-0412", "file": "admissions_2026_cse.csv", "uploadedBy": "P. Nair", "total": 182, "accepted": 176, "rejected": 6, "status": "Completed with errors"},
            {"id": "BATCH-0411", "file": "admissions_2026_mba.csv", "uploadedBy": "P. Nair", "total": 124, "accepted": 124, "rejected": 0, "status": "Completed"},
            {"id": "BATCH-0410", "file": "ece_lateral_entry.csv", "uploadedBy": "K. Rao", "total": 18, "accepted": 0, "rejected": 18, "status": "Failed"},
            {"id": "BATCH-0409", "file": "mechanical_2026.csv", "uploadedBy": "K. Rao", "total": 85, "accepted": 83, "rejected": 2, "status": "Completed with errors"},
            {"id": "BATCH-0408", "file": "mca_2026.csv", "uploadedBy": "P. Nair", "total": 58, "accepted": 58, "rejected": 0, "status": "Completed"},
        ]
        for b in demo_batches:
            batch = UploadBatch(
                id=b["id"],
                institution_id="INS-001",
                filename=b["file"],
                uploaded_by_name=b["uploadedBy"],
                status=b["status"],
                total=b["total"],
                accepted=b["accepted"],
                rejected=b["rejected"],
            )
            db.add(batch)
            if b["rejected"] > 0:
                for r in range(b["rejected"]):
                    err = UploadRowResult(
                        batch_id=batch.id,
                        row_number=4 + r * 7,
                        field=["apaar_id", "programme_code", "admission_category"][r % 3],
                        raw_value="•••• 9012" if r % 3 == 0 else "INVALID",
                        rule=["APAAR identifier must be 12 digits.", "Programme code is required.", "Category must be an approved category."][r % 3],
                        is_error=True,
                    )
                    db.add(err)
        db.commit()

        print("Seeding audit events...")
        demo_actions = [
            "Updated admission record",
            "Uploaded CSV batch",
            "Resolved finding",
            "Escalated finding",
            "Viewed student record",
            "Exported report",
            "Changed intake configuration",
            "Signed in",
            "Attempted role change",
        ]
        actors = ["P. Nair", "K. Rao", "R. Menon", "S. Kulkarni", "A. Verma"]
        roles = ["Institution admin", "Data officer", "Central reviewer", "Authorized verifier"]

        for i in range(40):
            act = random.choice(demo_actions)
            res = "Denied" if act == "Attempted role change" else ("Failed" if random.random() > 0.95 else "Success")
            target_ref = "—" if act == "Signed in" else (f"BATCH-{408 + i % 5}" if "CSV" in act else (f"FND-{2601 + i % 10}" if "finding" in act else f"STU-{1001 + i % 20}"))
            
            audit = AuditEvent(
                id=f"AUD-{9000 + i}",
                institution_id="INS-001",
                actor_name=random.choice(actors),
                actor_role=random.choice(roles),
                action=act,
                ref=target_ref,
                result=res,
                details="Synthetic audit log event for demo compliance check",
            )
            db.add(audit)
        db.commit()

        print("Database seeded successfully with synthetic demo data!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
