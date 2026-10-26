# SIH26263 — Security Model & Tenant Isolation

## 1. Authentication Architecture
- Password storage utilizes modern **Bcrypt** adaptive key derivation with individual salts.
- Authenticated sessions issue signed **JSON Web Tokens (JWT)** with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Tokens are transmitted via `Authorization: Bearer <token>` headers or browser `access_token` cookies with `HttpOnly` and `SameSite=Lax` protection.

## 2. Role-Based Access Control (RBAC) Matrix

| Permission | `institution_operator` | `institution_admin` | `central_reviewer` | `authorized_verifier` | `system_admin` |
|---|:---:|:---:|:---:|:---:|:---:|
| `students:view` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `students:create` | ✓ | ✓ | — | — | ✓ |
| `students:edit` | ✓ | ✓ | — | — | ✓ |
| `csv:import` | ✓ | ✓ | — | — | ✓ |
| `findings:view` | ✓ | ✓ | ✓ | — | ✓ |
| `findings:review` | — | ✓ | ✓ | — | ✓ |
| `intake:configure` | — | ✓ | — | — | ✓ |
| `apaar:verify` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `reports:export` | ✓ | ✓ | ✓ | — | ✓ |
| `audit:view` | — | ✓ | ✓ | — | ✓ |
| `institutions:manage` | — | — | — | — | ✓ |
| `roles:manage` | — | — | — | — | ✓ |

## 3. Strict Tenant Isolation
- **Tenant ID**: Every institution user belongs to an explicit `institution_id` (`INS-001`, `INS-002`, etc.).
- **Server-Side Enforcement**: All queries on `/students`, `/uploads`, `/findings`, `/intake-configuration`, and `/audit` enforce `WHERE institution_id = current_user.institution_id`.
- **Parameter Tampering Prevention**: Attempting to fetch or modify a record belonging to another institution immediately triggers an HTTP `403 Forbidden` response.
- **Automated Isolation Testing**: Automated test suite (`backend/tests/test_isolation.py`) explicitly validates that an admin from `INS-001` cannot read or tamper with student records belonging to `INS-002`.

## 4. Sensitive Identifier Masking & Hashing
- **Never Store Plaintext in Logs or URLs**: APAAR numbers are never logged in system outputs or passed as URL path parameters.
- **Masking Strategy**: The UI and API responses display masked identifiers (`•••• •••• {last4}`), obscuring the first 8 digits.
- **Salted Hash Matching**: Duplicate detection across records is performed using SHA-256 salted hashes (`apaar_hash`), enabling exact matches without exposing raw identity identifiers.

## 5. CSV Formula Injection Defense (CWE-1236)
Spreadsheet applications (Microsoft Excel, LibreOffice Calc) interpret leading characters like `=`, `+`, `-`, and `@` as executable formula macros.
- All exported CSV files and error reports process each cell through `sanitize_csv_cell()`.
- Dangerous characters are prefixed with a single quote (`'`), neutralizing macro execution upon opening in spreadsheet software.

## 6. Regulatory & Compliance Notice
> [!NOTE]
> Implementation of robust role controls, salted hashing, and audit trails represents essential defense-in-depth engineering. It does not constitute full regulatory certification or substitute for formal accreditation by AICTE, UIDAI, or Digilocker.
