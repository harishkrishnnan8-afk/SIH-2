import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.config import settings
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.admission import Admission
from backend.app.models.institution import Institution
from backend.app.models.intake import IntakeConfig
from backend.app.models.programme import Programme
from backend.app.models.student import Student
from backend.app.models.user import User

# Use separate test database
TEST_DB_URL = "sqlite:///./test_apaar.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        # Seed test institutions
        inst1 = Institution(id="INS-001", name="Test Institute 1", ref="TEST-AICTE-0001", state="Delhi", status="Active")
        inst2 = Institution(id="INS-002", name="Test Institute 2", ref="TEST-AICTE-0002", state="Maharashtra", status="Active")
        db.add_all([inst1, inst2])

        # Seed test programmes
        prog1 = Programme(code="BT-CSE", name="Computer Science", academic_year="2026–27", approved_intake=2, institution_id="INS-001")
        prog2 = Programme(code="BT-CSE", name="Computer Science", academic_year="2026–27", approved_intake=10, institution_id="INS-002")
        db.add_all([prog1, prog2])

        # Seed test intake configs
        intake1 = IntakeConfig(institution_id="INS-001", academic_year="2026–27", supernumerary_excluded=True)
        intake2 = IntakeConfig(institution_id="INS-002", academic_year="2026–27", supernumerary_excluded=True)
        db.add_all([intake1, intake2])

        # Seed test users
        admin_ins1 = User(
            id="U-ADMIN-1",
            username="admin1",
            email="admin1@test.edu",
            hashed_password=get_password_hash("Password@123"),
            full_name="Admin One",
            role="institution_admin",
            institution_id="INS-001",
        )
        admin_ins2 = User(
            id="U-ADMIN-2",
            username="admin2",
            email="admin2@test.edu",
            hashed_password=get_password_hash("Password@123"),
            full_name="Admin Two",
            role="institution_admin",
            institution_id="INS-002",
        )
        central_rev = User(
            id="U-CENTRAL",
            username="central1",
            email="central@test.gov",
            hashed_password=get_password_hash("Password@123"),
            full_name="Central Reviewer",
            role="central_reviewer",
            institution_id=None,
        )
        db.add_all([admin_ins1, admin_ins2, central_rev])
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_apaar.db"):
        try:
            os.remove("./test_apaar.db")
        except Exception:
            pass


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def token_admin_ins1():
    return create_access_token({"sub": "U-ADMIN-1", "role": "institution_admin", "institution_id": "INS-001"})


@pytest.fixture
def token_admin_ins2():
    return create_access_token({"sub": "U-ADMIN-2", "role": "institution_admin", "institution_id": "INS-002"})


@pytest.fixture
def token_central():
    return create_access_token({"sub": "U-CENTRAL", "role": "central_reviewer", "institution_id": None})
