export const TEMPLATE_HEADERS = ["student_name", "apaar_id", "programme_code", "academic_year", "admission_category", "admission_status", "date_of_birth"];

export interface RowError { row: number; field: string; value: string; rule: string }

export function parseCsv(text: string): string[][] {
  return text
    .split(/\r?\n/)
    .filter((l) => l.trim().length)
    .map((l) => l.split(",").map((c) => c.trim().replace(/^"|"$/g, "")));
}

const CATEGORIES = ["General", "Supernumerary", "NRI", "OCI", "Foreign National"];

export function validateRows(rows: string[][], mapping: Record<string, number>): { accepted: number; errors: RowError[] } {
  const errors: RowError[] = [];
  const seen = new Set<string>();
  let accepted = 0;
  rows.forEach((r, i) => {
    const row = i + 2;
    const val = (f: string) => (mapping[f] !== undefined && mapping[f] >= 0 ? r[mapping[f]] ?? "" : "");
    const before = errors.length;
    if (!val("student_name")) errors.push({ row, field: "student_name", value: "", rule: "Student name is required." });
    const id = val("apaar_id").replace(/\D/g, "");
    if (id.length !== 12) errors.push({ row, field: "apaar_id", value: id ? `••••${id.slice(-4)}` : "", rule: "APAAR identifier must be 12 digits." });
    else if (seen.has(id)) errors.push({ row, field: "apaar_id", value: `••••${id.slice(-4)}`, rule: "Identifier repeated within this file." });
    seen.add(id);
    const cat = val("admission_category");
    if (cat && !CATEGORIES.includes(cat)) errors.push({ row, field: "admission_category", value: cat, rule: `Category must be one of: ${CATEGORIES.join(", ")}.` });
    if (!val("programme_code")) errors.push({ row, field: "programme_code", value: "", rule: "Programme code is required." });
    if (errors.length === before) accepted++;
  });
  return { accepted, errors };
}

export function downloadCsv(filename: string, rows: (string | number)[][]) {
  const body = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([body], { type: "text/csv" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
