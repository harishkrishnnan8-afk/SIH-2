# SIH26263 — Requirements Traceability Matrix

| Requirement Area | Specification / Objective | Implementation Component | Automated Test Reference |
|---|---|---|---|
| **P0 Inspection** | Inspect Lovable frontend, routes, state & preserve design | `src/routes/*`, `src/components/*` | `bun run test`, `bun run build` |
| **P1 Backend** | FastAPI, Pydantic v2, SQLAlchemy, Alembic, SQLite/PostgreSQL | `backend/app/main.py`, `backend/app/config.py` | `backend/tests/conftest.py` |
| **P2 Data Model** | 14 Normalized entities, UUID identity, separation of student & admission | `backend/app/models/*.py`, `backend/alembic/versions/*` | `test_validation_engine.py`, `test_reviews.py` |
| **P3 Auth & RBAC** | Bcrypt hashing, JWT tokens, tenant isolation, role matrix | `backend/app/core/security.py`, `backend/app/core/permissions.py` | `test_auth.py`, `test_isolation.py` |
| **P4 CRUD APIs** | Full endpoints under `/api/v1` matching frontend | `backend/app/routers/*.py` | `test_students.py`, `test_dashboard.py` |
| **P5 CSV Ingestion** | Robust upload, header check, row errors, CWE-1236 formula defense | `backend/app/services/csv_service.py`, `backend/app/routers/uploads.py` | `test_csv_upload.py`, `src/test/csv.test.ts` |
| **P6 Rule Engine** | Deterministic explainable rules (format, duplicate, intake, category) | `backend/app/rules/engine.py`, `backend/app/rules/definitions.py` | `test_validation_engine.py` |
| **P7 Review & Audit** | Review actions (Resolve, Escalate, Request correction) & immutable audit trail | `backend/app/models/review.py`, `backend/app/core/audit.py` | `test_reviews.py` |
| **P8 Dashboard** | Live aggregation of student records, intake, and central reviewer metrics | `backend/app/routers/dashboard.py`, `backend/app/routers/reports.py` | `test_dashboard.py` |
| **P9 Verification** | Provider-adapter interface, simulated label disclaimer | `backend/app/verification/adapter.py`, `backend/app/verification/mock_provider.py` | `test_verification.py` |
| **P10 Frontend Integration** | Connected client, token storage, API routes, error toasts | `src/lib/api/client.ts`, `src/lib/services/index.ts` | Vitest & Vite client bundle build |
| **P11 Demo Data** | Repeatable seed script with synthetic institutions, programmes, students | `backend/app/seed/seed_data.py` | Verified against seed run |
| **P12 Automated Testing** | Backend unit/integration tests and frontend vitest suite | `backend/tests/*.py`, `src/test/*.ts` | 24 Pytest tests + 4 Vitest tests passing |
