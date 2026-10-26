# SIH26263 — Deterministic Validation Engine & Rule Catalog

## Design Philosophy
- Every validation outcome is **deterministic** and **explainable**.
- Findings contain concrete rule codes, categories, severity ratings, evidence citations, and recommended next steps.
- A duplicate finding or anomaly is **not proof of fraud**; the system flags discrepancies for human reviewer resolution and avoids automatic deletion or destructive merging.
- Intake calculations are **configurable** per academic year and institution.

---

## Rule Catalog

### 1. Attribute Completeness
- **`R-REQ-01`**: Student name is required (Severity: `Medium`).
  - *Explanation*: Empty or whitespace-only name field.
  - *Next steps*: Provide student's legal name according to secondary school certificate.
- **`R-REQ-02`**: Programme code is required and must exist (Severity: `High`).
  - *Explanation*: The provided programme code does not match active approved offerings for this institution.
  - *Next steps*: Reassign admission to an approved institution programme.
- **`R-REQ-04`**: Admission category is required (Severity: `Medium`).
  - *Explanation*: Category field is empty in upload or registration.
  - *Next steps*: Update category (General, Supernumerary, NRI, OCI, Foreign National).

### 2. Identifier Structure
- **`R-FMT-02`**: APAAR identifier must contain exactly 12 numeric digits (Severity: `Medium`).
  - *Explanation*: Identifier failed length or numeric format check.
  - *Next steps*: Request corrected identifier from student or admissions office.

### 3. Duplicate Detection
- **`R-DUP-01`**: Within-institution Name + Date of Birth duplicate match (Severity: `High`).
  - *Explanation*: Another active admission in this institution shares the identical full name and date of birth.
  - *Next steps*: Compare both physical admission files. Possible duplicate is not proof of fraud.
- **`R-DUP-02`**: Within-institution APAAR duplicate match (Severity: `High`).
  - *Explanation*: The APAAR identifier matches an existing registered student identity.
  - *Next steps*: Verify whether multiple admissions were assigned to the same individual.
- **`R-DUP-03`**: Identifier repeated within upload file (Severity: `High`).
  - *Explanation*: Identifier occurs multiple times in the uploaded CSV batch.
  - *Next steps*: Deduplicate batch rows before importing.
- **`R-CROSS-01`**: Cross-institution duplicate alert (Severity: `High`).
  - *Explanation*: An active student record in another institution shares the same APAAR hash.
  - *Next steps*: Escalate to central reviewer for cross-institution admission verification. Do not automatically cancel.

### 4. Admission Category & Quota Policies
- **`R-CAT-01`**: Invalid category value (Severity: `Medium`).
  - *Explanation*: Category is not in configured AICTE categories.
- **`R-CAT-03`**: OCI status confirmation missing (Severity: `Medium`).
  - *Explanation*: Student registered under OCI category without recorded OCI card number or confirmation.
  - *Next steps*: Attach OCI documentation or reassign admission category.

### 5. Intake Capacity & Overrun
- **`R-INT-01`**: Approved intake exceeded (Severity: `High`).
  - *Explanation*: Total enrolled students in programme exceeds approved intake.
  - *Next steps*: Confirm whether supernumerary seats apply under the institution's intake configuration.
- **`R-INT-WARN`**: Intake threshold warning (Severity: `Low`).
  - *Explanation*: Programme enrolment is at or above 95% of approved intake capacity.
  - *Next steps*: Monitor remaining vacancies before opening additional counseling rounds.
