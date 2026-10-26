# SIH26263 — API Contracts (/api/v1)

All endpoints are hosted under `/api/v1` and enforce HTTP Bearer authentication or `access_token` session cookies.

## Authentication & Authorization

### `POST /api/v1/auth/login`
- **Request Body**:
  ```json
  {
    "user": "priya.nair",
    "pass": "Password@123"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "USR-001",
      "username": "priya.nair",
      "email": "priya.nair@example.edu",
      "full_name": "Priya Nair",
      "role": "institution_admin",
      "institution_id": "INS-001",
      "institution_name": "Demo Institute of Technology, North Campus"
    }
  }
  ```
- Sets `access_token` HttpOnly cookie.

### `POST /api/v1/auth/logout`
- Clears session cookie and invalidates client session.

### `GET /api/v1/auth/me`
- Returns profile of currently authenticated user.

---

## Students & Admissions

### `GET /api/v1/students`
- **Query Parameters**:
  - `q`: Search string (name, record ID, last 4 digits)
  - `programme`: Filter by programme code (e.g. `BT-CSE` or `all`)
  - `status`: Filter by record status (`Verified`, `Pending review`, `Flagged`, `Draft`)
- **Tenant Scoping**: Automatically filtered by caller's `institution_id` (unless caller is `central_reviewer` or `system_admin`).
- **Response** (200 OK):
  ```json
  [
    {
      "id": "STU-1001",
      "name": "Aarav Sharma",
      "apaar": "•••• •••• 9012",
      "programme": "BT-CSE",
      "admissionYear": 2026,
      "category": "General",
      "status": "Verified",
      "updated": "2026-10-26T12:00:00Z",
      "dob": "2006-04-12",
      "gender": "Male",
      "email": "aarav.1001@example.edu",
      "institutionId": "INS-001"
    }
  ]
  ```

### `GET /api/v1/students/{id}`
- Returns student detail. Enforces tenant isolation: Returns `403 Forbidden` if caller attempts cross-institution access.

### `POST /api/v1/students`
- **Request Body**:
  ```json
  {
    "name": "Vihaan Patel",
    "apaar": "123456789012",
    "programme": "BT-CSE",
    "year": "2026–27",
    "category": "General",
    "status": "Admitted",
    "dob": "2006-05-18",
    "gender": "Male"
  }
  ```
- Evaluates deterministic validation engine. Persists student, admission record, and findings atomically.
- **Response** (200 OK):
  ```json
  {
    "persisted": true,
    "student_id": "STU-1065",
    "findings_count": 0,
    "message": "Student identity and admission record persisted successfully."
  }
  ```

---

## CSV Ingestion

### `GET /api/v1/uploads`
- Returns list of historical import batches.

### `POST /api/v1/uploads`
- Multipart file upload (`.csv`, max 15MB).
- Validates UTF-8 encoding, required headers (`student_name`, `apaar_id`, `programme_code`), row constraints, and checks duplicates.
- **Response** (200 OK):
  ```json
  {
    "accepted": 176,
    "rejected": 6,
    "total": 182,
    "errors": [
      {
        "row": 4,
        "field": "apaar_id",
        "value": "•••• 1234",
        "rule": "APAAR identifier must be exactly 12 digits."
      }
    ],
    "batch_id": "BATCH-0412",
    "persisted": true
  }
  ```

### `GET /api/v1/uploads/{batch_id}/errors.csv`
- Downloads row-level error report in CSV format. Sanitizes cells against CSV injection.

---

## Validation Findings & Reviews

### `GET /api/v1/findings`
- Returns open, under review, resolved, and escalated findings.

### `POST /api/v1/findings/{id}/actions`
- **Request Body**:
  ```json
  {
    "action": "Resolve",
    "note": "Verified with original physical admission dossier."
  }
  ```
- Allowed actions: `Start review`, `Request correction`, `Escalate`, `Resolve`.
- Generates an immutable `AuditEvent`.

---

## Verification Integration

### `POST /api/v1/verification/verify`
- **Request Body**:
  ```json
  {
    "id": "123456789012"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "mode": "simulated",
    "formatValid": true,
    "internalMatch": true,
    "providerStatus": "Mock provider",
    "checkedAt": "2026-10-26T14:40:00Z",
    "isSimulated": true,
    "simulationLabel": "SIMULATED — NOT OFFICIAL APAAR VERIFICATION",
    "student": {
      "id": "STU-1001",
      "name": "Aarav Sharma",
      "apaar": "•••• •••• 9012"
    }
  }
  ```

---

## Governance & Reports

### `GET /api/v1/reports/data?key={enrolment|intake|findings|imports|quality|audit}`
- Returns live tabular aggregated report rows.

### `GET /api/v1/reports/export?key={key}`
- Returns CSV file with top disclaimer `DEMO ENVIRONMENT — SYNTHETIC DATA` and sanitized cells.

### `GET /api/v1/audit`
- Lists audit trail events scoped to institution.
