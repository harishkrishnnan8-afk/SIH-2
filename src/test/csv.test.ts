import { describe, expect, it } from "vitest";
import { validateRows } from "@/lib/csv";
import { maskApaar } from "@/lib/api/client";

const map = { student_name: 0, apaar_id: 1, programme_code: 2, admission_category: 3 };

describe("CSV validation", () => {
  it("rejects identifiers that are not 12 digits", () => {
    const r = validateRows([["A", "12345", "BT-CSE", "General"]], map);
    expect(r.accepted).toBe(0);
    expect(r.errors[0]?.field).toBe("apaar_id");
  });
  it("rejects a repeated identifier within the file", () => {
    const r = validateRows([["A", "123456789012", "BT-CSE", "General"], ["B", "123456789012", "BT-CSE", "General"]], map);
    expect(r.accepted).toBe(1);
  });
  it("masks all but the last 4 digits", () => {
    expect(maskApaar("123456789012")).toBe("•••• •••• 9012");
  });
});
