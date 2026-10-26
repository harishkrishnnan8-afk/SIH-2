import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader, Section, th, td, tr } from "@/components/app/primitives";
import { students, programmes, findings, imports, audit } from "@/lib/demo/data";
import { downloadCsv } from "@/lib/csv";
import { cn } from "@/lib/utils";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/reports")({
  head: pageHead("Reports & exports", "Preview and export enrolment, intake, findings, import, data-quality and audit reports."),
  component: Reports,
});

type Rows = (string | number)[][];
const REPORTS: { key: string; title: string; build: () => Rows }[] = [
  { key: "enrolment", title: "Student enrolment", build: () => [["Programme", "Enrolled"], ...programmes.map((p) => [p.code, p.actualEnrolment])] },
  { key: "intake", title: "Intake utilisation", build: () => [["Programme", "Approved", "Enrolled", "Utilisation %"], ...programmes.map((p) => [p.code, p.approvedIntake, p.actualEnrolment, Math.round((p.actualEnrolment / p.approvedIntake) * 100)])] },
  { key: "findings", title: "Validation findings", build: () => [["Reference", "Category", "Severity", "Status"], ...findings.map((f) => [f.id, f.category, f.severity, f.status])] },
  { key: "imports", title: "CSV import summary", build: () => [["Batch", "File", "Accepted", "Rejected"], ...imports.map((b) => [b.id, b.file, b.accepted, b.rejected])] },
  { key: "quality", title: "Institutional data quality", build: () => { const s = ["Verified", "Pending review", "Flagged", "Correction requested", "Draft"]; return [["Status", "Records"], ...s.map((x) => [x, students.filter((y) => y.status === x).length])]; } },
  { key: "audit", title: "Audit activity", build: () => [["Timestamp", "Actor", "Action", "Result"], ...audit.slice(0, 20).map((a) => [a.at, a.actor, a.action, a.result])] },
];

function Reports() {
  const [sel, setSel] = useState("enrolment");
  const [year, setYear] = useState("2026–27");
  const [loading, setLoading] = useState(false);
  const r = REPORTS.find((x) => x.key === sel) ?? REPORTS[0]!;
  const rows = r.build();
  const head = (rows[0] ?? []).map(String);
  const choose = (k: string) => { setSel(k); setLoading(true); setTimeout(() => setLoading(false), 350); };

  return (
    <>
      <PageHeader crumbs={[{ label: "Verification & Reporting" }, { label: "Reports & Exports" }]} title="Reports & exports" description="Exports contain synthetic demo data and are marked accordingly." />
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <nav aria-label="Reports" className="space-y-0.5">
          {REPORTS.map((x) => <button key={x.key} onClick={() => choose(x.key)} className={cn("block w-full rounded-sm px-3 py-2 text-left text-sm transition-colors", sel === x.key ? "bg-surface font-medium shadow-subtle ring-1 ring-border" : "text-muted-foreground hover:bg-surface hover:text-foreground")}>{x.title}</button>)}
        </nav>
        <Section title={r.title} description={`Preview · Academic year ${year}`} actions={
          <div className="flex gap-2">
            <Select value={year} onValueChange={setYear}><SelectTrigger className="h-8 w-32" aria-label="Academic year"><SelectValue /></SelectTrigger><SelectContent>{["2026–27", "2025–26"].map((y) => <SelectItem key={y} value={y}>{y}</SelectItem>)}</SelectContent></Select>
            <Button size="sm" disabled={loading} onClick={() => { downloadCsv(`DEMO_${r.key}_report.csv`, [["DEMO ENVIRONMENT — SYNTHETIC DATA"], ...rows]); toast.success("CSV exported"); }}>{loading ? <Loader2 className="size-4 animate-spin" /> : <Download className="size-4" />} Export CSV</Button>
          </div>
        }>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr>{head.map((h) => <th key={h} className={th}>{h}</th>)}</tr></thead>
              <tbody>{loading ? Array.from({ length: 5 }).map((_, i) => <tr key={i} className="border-t">{head.map((_, j) => <td key={j} className={td}><Skeleton className="h-4" /></td>)}</tr>) : rows.slice(1).map((row, i) => <tr key={i} className={tr}>{row.map((c, j) => <td key={j} className={`${td} tabular-nums`}>{c}</td>)}</tr>)}</tbody>
            </table>
          </div>
        </Section>
      </div>
    </>
  );
}
