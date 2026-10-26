# SIH26263 — Demonstration Script

This script walks through the end-to-end evaluation flow demonstrating each required milestone.

---

## Demo Accounts

All demo accounts share the password: `Password@123`

| Role | Username / Email | Institution | Purpose |
|---|---|---|---|
| **Institution Admin** | `priya.nair` or `priya.nair@example.edu` | `INS-001` (Demo Institute of Technology) | Full institution management, student creation, CSV import, findings review, reports |
| **Data Officer** | `k.rao` or `k.rao@example.edu` | `INS-001` | Data entry & CSV upload |
| **Central Reviewer** | `r.menon` or `r.menon@aicte.gov.in` | None (Central AICTE Scope) | Multi-institution aggregated dashboard, cross-institution duplicate review |
| **Authorized Verifier** | `s.kulkarni` or `s.kulkarni@example.edu` | `INS-001` | Fast APAAR lookup and verification checks |
| **Institution Admin 2** | `admin.ins002` or `admin@sample.edu` | `INS-002` (Sample College of Engineering) | Used to demonstrate strict tenant data isolation |

---

## Step-by-Step Walkthrough

### 1. Sign In
1. Open the platform at `http://localhost:5173/login`.
2. Enter username `priya.nair` and password `Password@123`.
3. Click **Sign in**. The user is authenticated, the backend issues a signed JWT, logs an audit event, and directs to the Institutional Dashboard.

### 2. Institutional Dashboard & Live Database Aggregates
1. View the 4 summary metrics cards:
   - Total student records
   - Actual enrolment
   - Approved intake
   - Records requiring review
2. Notice that figures are computed live from the SQLite/PostgreSQL database records, not hardcoded mock numbers.
3. Review the **Enrolment vs. approved intake** chart showing capacity utilization across B.Tech, MBA, and MCA programmes.

### 3. Student Registration & Deterministic Rule Engine
1. Navigate to **Students** -> click **Register student** (`/students/new`).
2. Register a new student:
   - Full Name: `Aarav Sharma`
   - APAAR ID: `123456789012`
   - Programme: `BT-CSE`
   - Academic Year: `2026–27`
   - Admission Category: `General`
3. Click **Save student**.
4. The backend validates 12 digits, checks within-institution duplicate rules, persists the student with an internal UUID, and records an audit log. Notice toast notification confirming database persistence.

### 4. CSV Bulk Ingestion & Error Reporting
1. Navigate to **CSV Imports** (`/uploads`).
2. Download the template by clicking **Download template**.
3. Upload a sample CSV containing both valid and intentionally flawed records (e.g., malformed 5-digit APAAR, missing name).
4. Review the column mapping screen, then click **Validate records**.
5. The backend validates each row, saves accepted students, records row-level errors, and displays:
   - Rows checked
   - Passed validation
   - Rejected count
   - Row-level error table
6. Click **Error report** to download the sanitized error CSV.

### 5. Validation Finding Review Workflow
1. Navigate to **Validation Findings** (`/findings`).
2. Click on finding `FND-2601` or another open finding to view details.
3. Review the **Triggered rule**, **Supporting evidence**, and **Next steps**.
4. Click **Start review**, enter a note, and confirm.
5. Click **Resolve**, enter explanation `"Confirmed against original physical dossier"`, and submit.
6. The finding status updates to `Resolved` and a tamper-resistant entry is written to the audit trail.

### 6. Verification Provider Interface
1. Navigate to **Verification** (`/verification`).
2. Observe the prominent warning banner:
   **SIMULATED — NOT OFFICIAL APAAR VERIFICATION**
3. Click the sample identifier to populate the 12-digit number.
4. Click **Verify**.
5. The adapter runs format validation, internal database record matching, and simulated provider verification, returning structured results with transparent simulation disclaimers.

### 7. Governance & Audit Trail
1. Navigate to **Audit Trail** (`/audit`).
2. View the chronological, immutable audit log:
   - Login events
   - Student admissions
   - CSV uploads
   - Finding resolutions
   - Verification attempts
3. Notice that full student identifiers are masked to protect student privacy.

### 8. Central Reviewer Dashboard
1. Sign out and log in as `r.menon` (Password: `Password@123`).
2. Navigate to **Central Review** (`/central`).
3. View aggregated statistics across all AICTE-approved institutions in scope, intake utilization percentages, outstanding findings, and data quality scores.

### 9. Tenant Isolation Verification
1. Log in as `priya.nair` (`INS-001`).
2. Attempting to access an `INS-002` student record (e.g. `STU-9999`) returns `403 Forbidden`.
3. Cross-institution access cannot be gained by altering URL IDs or parameters.
