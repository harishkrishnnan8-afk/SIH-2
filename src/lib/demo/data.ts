// DEMO ENVIRONMENT — SYNTHETIC DATA. Every record here is fictional.
export type RecordStatus = "Verified" | "Pending review" | "Flagged" | "Draft" | "Correction requested";
export type Category = "General" | "Supernumerary" | "NRI" | "OCI" | "Foreign National";
export type Severity = "High" | "Medium" | "Low";
export type FindingStatus = "Open" | "Under review" | "Resolved" | "Escalated";

export interface Programme { code: string; name: string; year: string; approvedIntake: number; actualEnrolment: number; institutionId: string; policy: string }
export interface Institution { id: string; name: string; ref: string; status: "Active" | "Under review" | "Suspended"; state: string }
export interface Student {
  id: string; name: string; apaar: string; programme: string; admissionYear: number; category: Category;
  status: RecordStatus; updated: string; dob: string; gender: string; email: string; institutionId: string;
}
export interface Finding {
  id: string; studentId: string; category: string; severity: Severity; detected: string; status: FindingStatus;
  reviewer?: string | undefined; rule: string; evidence: string; nextSteps: string;
}
export interface ImportBatch { id: string; file: string; uploadedBy: string; at: string; total: number; accepted: number; rejected: number; status: "Completed" | "Completed with errors" | "Failed" | "Processing" }
export interface AuditEntry { id: string; at: string; actor: string; role: string; action: string; ref: string; result: "Success" | "Denied" | "Failed" }

let seed = 26263;
const rand = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
const pick = <T,>(a: readonly T[]): T => a[Math.floor(rand() * a.length)] as T;

export const institutions: Institution[] = [
  { id: "INS-001", name: "Demo Institute of Technology, North Campus", ref: "DEMO-AICTE-0001", status: "Active", state: "Delhi" },
  { id: "INS-002", name: "Sample College of Engineering", ref: "DEMO-AICTE-0002", status: "Active", state: "Maharashtra" },
  { id: "INS-003", name: "Example School of Management", ref: "DEMO-AICTE-0003", status: "Under review", state: "Karnataka" },
  { id: "INS-004", name: "Placeholder Polytechnic", ref: "DEMO-AICTE-0004", status: "Active", state: "Tamil Nadu" },
  { id: "INS-005", name: "Synthetic University of Applied Sciences", ref: "DEMO-AICTE-0005", status: "Suspended", state: "Gujarat" },
];

export const programmes: Programme[] = [
  { code: "BT-CSE", name: "B.Tech Computer Science & Engineering", year: "2026–27", approvedIntake: 180, actualEnrolment: 176, institutionId: "INS-001", policy: "Supernumerary excluded" },
  { code: "BT-ECE", name: "B.Tech Electronics & Communication", year: "2026–27", approvedIntake: 120, actualEnrolment: 104, institutionId: "INS-001", policy: "Supernumerary excluded" },
  { code: "BT-ME", name: "B.Tech Mechanical Engineering", year: "2026–27", approvedIntake: 120, actualEnrolment: 83, institutionId: "INS-001", policy: "Pending confirmation" },
  { code: "BT-CE", name: "B.Tech Civil Engineering", year: "2026–27", approvedIntake: 60, actualEnrolment: 47, institutionId: "INS-001", policy: "Supernumerary excluded" },
  { code: "MBA", name: "Master of Business Administration", year: "2026–27", approvedIntake: 120, actualEnrolment: 124, institutionId: "INS-001", policy: "NRI counted separately" },
  { code: "MCA", name: "Master of Computer Applications", year: "2026–27", approvedIntake: 60, actualEnrolment: 58, institutionId: "INS-001", policy: "Supernumerary excluded" },
];

const first = ["Aarav", "Ananya", "Vihaan", "Diya", "Arjun", "Isha", "Kabir", "Meera", "Rohan", "Saanvi", "Aditya", "Kavya", "Nikhil", "Priya", "Rahul", "Sneha", "Tanvi", "Yash", "Zoya", "Farhan"];
const last = ["Sharma", "Iyer", "Reddy", "Patel", "Nair", "Gupta", "Khan", "Das", "Menon", "Singh", "Joshi", "Bose", "Rao", "Mehta", "Pillai"];
const statuses: RecordStatus[] = ["Verified", "Verified", "Verified", "Pending review", "Pending review", "Flagged", "Draft", "Correction requested"];
const cats: Category[] = ["General", "General", "General", "General", "Supernumerary", "NRI", "OCI", "Foreign National"];

export const students: Student[] = Array.from({ length: 64 }, (_, i) => {
  const n = `${pick(first)} ${pick(last)}`;
  const d = new Date(2026, 9, 26 - Math.floor(rand() * 40), 9 + Math.floor(rand() * 8), Math.floor(rand() * 60));
  return {
    id: `STU-${String(1001 + i)}`,
    name: n,
    apaar: String(100000000000 + Math.floor(rand() * 899999999999)),
    programme: pick(programmes).code,
    admissionYear: pick([2023, 2024, 2025, 2026, 2026]),
    category: pick(cats),
    status: pick(statuses),
    updated: d.toISOString(),
    dob: `200${Math.floor(rand() * 7)}-0${1 + Math.floor(rand() * 9)}-1${Math.floor(rand() * 9)}`,
    gender: pick(["Female", "Male"]),
    email: `${(n.split(" ")[0] ?? "").toLowerCase()}.${i}@example.edu`,
    institutionId: "INS-001",
  };
});

const findingTypes = [
  { category: "Possible duplicate", rule: "R-DUP-01: Two records share the same name and date of birth within one institution.", evidence: "Name and date of birth match another active record in this programme.", nextSteps: "Compare both records with admission documents. A possible duplicate is not proof of fraud." },
  { category: "Identifier format", rule: "R-FMT-02: APAAR identifier must contain exactly 12 digits.", evidence: "Submitted identifier failed the format check during import.", nextSteps: "Request a corrected identifier from the student or admissions office." },
  { category: "Intake exceeded", rule: "R-INT-01: Enrolment in a programme exceeds the configured approved intake.", evidence: "Programme enrolment is above the configured approved intake value.", nextSteps: "Confirm whether supernumerary seats apply under the intake configuration." },
  { category: "Missing attribute", rule: "R-REQ-04: Admission category is required for all admitted students.", evidence: "Admission category field was empty in the uploaded row.", nextSteps: "Update the admission record with the correct category." },
  { category: "Category mismatch", rule: "R-CAT-03: OCI status must be confirmed for OCI category admissions.", evidence: "Record is marked OCI category but OCI status is not confirmed.", nextSteps: "Request a correction or attach confirmation." },
];
const fStatus: FindingStatus[] = ["Open", "Open", "Under review", "Resolved", "Escalated"];
export const findings: Finding[] = Array.from({ length: 28 }, (_, i) => {
  const t = pick(findingTypes);
  const st = pick(fStatus);
  return {
    id: `FND-${String(2601 + i)}`,
    studentId: pick(students).id,
    ...t,
    severity: t.category === "Possible duplicate" || t.category === "Intake exceeded" ? "High" : pick(["Medium", "Low"] as Severity[]),
    detected: new Date(2026, 9, 26 - Math.floor(rand() * 14), 8 + Math.floor(rand() * 9), 12).toISOString(),
    status: st,
    reviewer: st === "Open" ? undefined : pick(["R. Menon", "S. Kulkarni", "A. Verma"]),
  };
});

export const imports: ImportBatch[] = [
  { id: "BATCH-0412", file: "admissions_2026_cse.csv", uploadedBy: "P. Nair", at: "2026-10-26T08:42:00Z", total: 182, accepted: 176, rejected: 6, status: "Completed with errors" },
  { id: "BATCH-0411", file: "admissions_2026_mba.csv", uploadedBy: "P. Nair", at: "2026-10-25T11:05:00Z", total: 124, accepted: 124, rejected: 0, status: "Completed" },
  { id: "BATCH-0410", file: "ece_lateral_entry.csv", uploadedBy: "K. Rao", at: "2026-10-23T14:20:00Z", total: 18, accepted: 0, rejected: 18, status: "Failed" },
  { id: "BATCH-0409", file: "mechanical_2026.csv", uploadedBy: "K. Rao", at: "2026-10-22T09:12:00Z", total: 85, accepted: 83, rejected: 2, status: "Completed with errors" },
  { id: "BATCH-0408", file: "mca_2026.csv", uploadedBy: "P. Nair", at: "2026-10-20T10:30:00Z", total: 58, accepted: 58, rejected: 0, status: "Completed" },
];

const actions = ["Updated admission record", "Uploaded CSV batch", "Resolved finding", "Escalated finding", "Viewed student record", "Exported report", "Changed intake configuration", "Signed in", "Attempted role change"];
export const audit: AuditEntry[] = Array.from({ length: 40 }, (_, i) => {
  const a = pick(actions);
  return {
    id: `AUD-${9000 + i}`,
    at: new Date(2026, 9, 26, 18 - Math.floor(i / 3), 59 - (i * 7) % 60).toISOString(),
    actor: pick(["P. Nair", "K. Rao", "R. Menon", "S. Kulkarni", "A. Verma"]),
    role: pick(["Institution admin", "Data officer", "Reviewer"]),
    action: a,
    ref: a.includes("CSV") ? pick(imports).id : a.includes("finding") ? pick(findings).id : a.includes("intake") ? "CFG-INTAKE" : a === "Signed in" ? "—" : pick(students).id,
    result: a === "Attempted role change" ? "Denied" : rand() > 0.95 ? "Failed" : "Success",
  };
});

const agg: [number, number, number, string, number][] = [
  [592, 660, 14, "Submitted", 94], [1340, 1380, 22, "Submitted", 91], [412, 480, 31, "In progress", 78], [286, 300, 3, "Submitted", 97], [905, 960, 47, "Not started", 62],
];
export const centralInstitutions = institutions.map((ins, i) => {
  const [enrolment, intake, findings, submission, quality] = agg[i] ?? [0, 0, 0, "Not started", 0];
  return { ...ins, enrolment, intake, findings, submission, quality };
});
