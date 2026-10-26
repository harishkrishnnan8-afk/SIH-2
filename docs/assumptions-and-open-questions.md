# SIH26263 — Assumptions & Open Questions

## 1. Domain Assumptions

1. **APAAR Format**:
   - The platform assumes standard 12-digit numeric APAAR identifiers.
   - Format validation checks 12 numeric digits; it does not constitute algorithmic verification of official UIDAI/DigiLocker authenticity.
2. **Identity vs. Admission History**:
   - A student possesses one lifelong academic identity (APAAR), which is separate from individual admission records across programmes, institutions, and academic years.
3. **Intake Policy Flexibility**:
   - Treatment of supernumerary seats (e.g. AICTE Tuition Fee Waiver, PMSSS, lateral entry), NRI quotas, and Foreign Nationals varies by institution and state regulatory guidelines.
   - The platform makes supernumerary exclusion configurable per institution via `IntakeConfig` rather than hardcoding business rules.
4. **Duplicate Handling**:
   - A duplicate match (same APAAR or same name + DOB) triggers a review finding (`R-DUP-01`, `R-DUP-02`) rather than automatically discarding or merging records. Human review with official records is mandatory.

## 2. Policy & Regulatory Open Questions

1. **Official Verification Gateway Access**:
   - Official API integration with the AICTE/DigiLocker/APAAR gateway requires approved institutional credentials and cryptographic certificates.
   - In the absence of live gateway credentials, the platform operates with a clean adapter interface and an explicit mock provider displaying:
     `SIMULATED — NOT OFFICIAL APAAR VERIFICATION`
2. **Data Retention & Archival**:
   - Standard AICTE regulations for long-term retention of rejected upload logs and audit trails must be established per institutional guidelines.
3. **Cross-Institution Resolution Workflow**:
   - When a cross-institution duplicate (`R-CROSS-01`) is flagged, current implementation escalates the finding to the `central_reviewer`. Clarification is needed on whether automated cross-institutional notification or multi-party reconciliation workflows should be initiated.
