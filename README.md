# SIH26263 — APAAR ID-Based Student Data Management & Verification Platform
### For AICTE Approved Institutions (Smart India Hackathon)

This repository contains the full-stack platform for **SIH26263**: an APAAR ID-based student data management, intake compliance, and verification system for AICTE-approved institutions.

The project combines a TanStack Start / React 19 frontend with a Python FastAPI modular monolith backend, deterministic validation engine, normalized database schema, and strict tenant isolation.

---

## Architecture & Technology Stack

- **Frontend**: TanStack Start, React 19, Tailwind CSS v4, Lucide Icons, Recharts, TanStack Query
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- **Database**: SQLite (zero-configuration local evaluation) or PostgreSQL (production ready)
- **Security**: Bcrypt password hashing, JWT session authentication, tenant isolation, CWE-1236 CSV injection sanitization, identifier masking (`•••• •••• {last4}`)
- **Testing**: Pytest (backend 24 automated unit & integration tests) + Vitest (frontend client tests)

---

## One-Click Windows Management

For Windows users, three turnkey batch files are provided in the project root:

| Script | Purpose | Description |
|---|---|---|
| **`start.bat`** | **Start System** | Checks dependencies, starts the FastAPI backend (port 8000) and Vite frontend (port 8080) in separate persistent terminal windows, waits for health readiness, and automatically opens the application in your browser. |
| **`stop.bat`** | **Stop System** | Gracefully stops the frontend and backend services using dedicated PID and port tracking without killing unrelated applications or deleting data. |
| **`restart.bat`** | **Restart System** | Safely shuts down running services, verifies ports 8000 and 8080 are released, and restarts the entire application cleanly. |

### How to Use:
1. Double-click **`start.bat`** to start both services. Once ready, your browser will open to `http://localhost:8080/login`.
2. Inspect live logs in the two opened console windows (`APAAR Backend` and `APAAR Frontend`).
3. Double-click **`stop.bat`** when you want to safely shut down all services.
4. Double-click **`restart.bat`** if you make configuration changes or wish to reboot both services.

---

## Quick Start & Local Run Instructions

### 1. Prerequisites
- **Node.js** (v18+) or **Bun** (v1.3+)
- **Python** (v3.10+)

### 2. Manual Backend Setup & Startup
```powershell
# From the repository root
# 1. Create and activate virtual environment (if not already created)
python -m venv backend/.venv
backend\.venv\Scripts\activate

# 2. Install dependencies
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings sqlalchemy alembic pyjwt cryptography bcrypt python-multipart pytest pytest-asyncio httpx

# 3. Apply database migrations
alembic upgrade head

# 4. Seed repeatable synthetic demo data
python -m backend.app.seed.seed_data

# 5. Start the backend API server (runs on port 8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: `http://127.0.0.1:8000/api/v1/docs`

### 3. Manual Frontend Setup & Startup
In a separate terminal window:
```powershell
# Install frontend dependencies
bun install   # or: npm install

# Start the Vite development server (runs on port 8080)
bun run dev   # or: npm run dev
```
Open your browser at `http://localhost:8080` (or `http://localhost:8080/login`).

---

## Demo Accounts

All demo accounts share the password: **`Password@123`**

| Role | Username / Email | Institution | Purpose |
|---|---|---|---|
| **Institution Admin** | `priya.nair` or `priya.nair@example.edu` | `INS-001` (Demo Institute of Technology) | Full institution management, student creation, CSV import, findings review, reports |
| **Data Officer** | `k.rao` or `k.rao@example.edu` | `INS-001` | Data entry & CSV upload |
| **Central Reviewer** | `r.menon` or `r.menon@aicte.gov.in` | None (Central AICTE Scope) | Multi-institution aggregated dashboard, cross-institution duplicate review |
| **Authorized Verifier** | `s.kulkarni` or `s.kulkarni@example.edu` | `INS-001` | Fast APAAR lookup and verification checks |
| **Institution Admin 2** | `admin.ins002` or `admin@sample.edu` | `INS-002` (Sample College of Engineering) | Used to demonstrate strict tenant data isolation |

---

## Running Automated Tests

### Run Backend Tests (24 tests)
```powershell
$env:PYTHONPATH="."
backend\.venv\Scripts\pytest.exe backend/tests
```
Verifies deterministic validation rules (`R-REQ-01`, `R-FMT-02`, `R-DUP-01`, `R-CROSS-01`, `R-INT-01`), tenant data isolation (403 Forbidden on cross-institution access), CSV injection prevention, review state machine, and mock verification provider.

### Run Frontend Tests
```powershell
bun run test   # or: npm run test
```

### Validate Production Bundle Build
```powershell
bun run build  # or: npm run build
```

---

## Documentation Links

Comprehensive engineering documentation is available in the [`docs/`](file:///docs/) directory:
- [Requirements Traceability Matrix](file:///docs/requirements-traceability.md)
- [System Architecture](file:///docs/architecture.md)
- [Database Schema & Data Model](file:///docs/data-model.md)
- [API Contracts (`/api/v1`)](file:///docs/api-contract.md)
- [Security Model & Tenant Isolation](file:///docs/security-model.md)
- [CSV Ingestion Pipeline](file:///docs/csv-import.md)
- [Deterministic Validation Rules](file:///docs/validation-rules.md)
- [Testing & Evaluation Guide](file:///docs/testing-and-evaluation.md)
- [Demonstration Script](file:///docs/demo-script.md)
- [Assumptions & Open Questions](file:///docs/assumptions-and-open-questions.md)

---

## Notice Regarding Verification & Simulation
> [!IMPORTANT]
> Official external verification with AICTE, APAAR, or DigiLocker requires authorized government gateway credentials and cryptographic certificates. In accordance with platform governance, all simulated mock responses are prominently labelled:
> **SIMULATED — NOT OFFICIAL APAAR VERIFICATION**
