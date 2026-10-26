# SIH26263 — Testing & Evaluation Guide

## Overview of Automated Test Suites

The project includes dual automated test suites covering both the Python FastAPI backend and the React/TypeScript frontend.

### 1. Backend Test Suite (Pytest)
Tests 24 individual scenarios across unit rules, tenant isolation, and integration workflows:
- **`test_validation_engine.py`**:
  - `test_apaar_masking`: Verifies 12-digit masking reveals only last 4 digits.
  - `test_csv_formula_injection_sanitization`: Verifies CWE-1236 macro neutralization.
  - `test_rule_r_fmt_02_invalid_apaar`: Verifies invalid APAAR lengths generate finding.
  - `test_rule_r_req_01_missing_name`: Rejects empty student names.
  - `test_rule_r_cat_01_invalid_category`: Rejects non-AICTE categories.
  - `test_rule_r_dup_01_same_name_and_dob`: Flags intra-institution identity duplicates.
  - `test_rule_r_cross_01_cross_institution_match`: Flags cross-institution collision.
  - `test_rule_r_int_01_intake_exceeded`: Flags intake capacity overruns.
- **`test_isolation.py`**:
  - `test_cross_institution_student_access_is_forbidden`: Admin 1 attempting to view Admin 2's student gets `403 Forbidden`.
  - `test_student_list_filters_by_institution_automatically`: Automatic tenant scoping.
  - `test_unauthenticated_request_is_denied`: Deny-by-default returns `401 Unauthorized`.
- **`test_auth.py`**:
  - `test_login_success`, `test_login_invalid_password`, `test_login_nonexistent_user`, `test_get_current_user_profile`, `test_logout_clears_cookie`.
- **`test_csv_upload.py`**:
  - `test_upload_valid_csv`: Full persistence of valid batch.
  - `test_upload_invalid_rows_returns_row_level_errors`: Detailed row-level error reporting.
  - `test_download_row_errors_csv`: Error CSV download with safe formula sanitization.
- **`test_reviews.py`**:
  - `test_review_action_state_transition_and_audit`: Verifies review state transitions (`Start review` -> `Escalate` -> `Resolve`) and audit log persistence.
- **`test_verification.py`**:
  - `test_verification_simulation_label`: Verifies simulated banner disclaimer.
  - `test_verification_invalid_format`: Verifies format failure handling.
- **`test_dashboard.py`**:
  - `test_central_dashboard_aggregation`: Real multi-institution metrics calculation.
  - `test_reports_data_and_export`: Live report preview and CSV export.

### Running Backend Tests
```powershell
$env:PYTHONPATH="."
backend\.venv\Scripts\pytest.exe backend/tests
```

### 2. Frontend Test Suite (Vitest)
- **`csv.test.ts`**: Verifies client-side CSV parsing, 12-digit format check, and identifier masking.
- **`app-routing.test.tsx`**: Verifies root layout matching and router configuration.

### Running Frontend Tests
```powershell
bun run test
# Or: npm run test
```
