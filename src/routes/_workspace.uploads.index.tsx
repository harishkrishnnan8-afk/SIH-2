import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useRef, useState, type DragEvent } from "react";
import { Upload, Download, FileText, Check, AlertTriangle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader, Section, StatusBadge, fmtDate, th, td, tr } from "@/components/app/primitives";
import { importsQuery, uploadCsvFile } from "@/lib/services";
import { BACKEND_CONNECTED } from "@/lib/api/client";
import { TEMPLATE_HEADERS, parseCsv, validateRows, downloadCsv, type RowError } from "@/lib/csv";
import { cn } from "@/lib/utils";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/uploads/")({
  head: pageHead("CSV imports", "Upload, map, validate and review student data CSV imports."),
  loader: ({ context }) => context.queryClient.ensureQueryData(importsQuery()),
  component: Uploads,
});

const STEPS = ["Upload CSV", "Map columns", "Validate records", "Review results"];

function Uploads() {
  const { data: batches } = useSuspenseQuery(importsQuery());
  const [step, setStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [headers, setHeaders] = useState<string[]>([]);
  const [rows, setRows] = useState<string[][]>([]);
  const [mapping, setMapping] = useState<Record<string, number>>({});
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<{ accepted: number; errors: RowError[] } | null>(null);
  const [drag, setDrag] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  const reset = () => { setStep(0); setFile(null); setError(null); setResult(null); setProgress(0); };

  const accept = async (f: File) => {
    setError(null);
    if (!f.name.toLowerCase().endsWith(".csv")) return setError("This file is not a CSV. Please upload a .csv file.");
    if (batches.some((b) => b.file === f.name)) toast.warning("Possible duplicate upload", { description: `A file named ${f.name} was imported before.` });
    const parsed = parseCsv(await f.text());
    if (parsed.length < 2) return setError("The file is empty or contains only a header row.");
    const [h = [], ...r] = parsed;
    setFile(f); setHeaders(h); setRows(r);
    setMapping(Object.fromEntries(TEMPLATE_HEADERS.map((t) => [t, h.findIndex((x) => x.toLowerCase() === t)])));
    setStep(1);
  };

  const onDrop = (e: DragEvent) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) accept(f); };

  const runValidation = async () => {
    setStep(2); setProgress(25);
    if (BACKEND_CONNECTED && file) {
      try {
        setProgress(50);
        const res = await uploadCsvFile(file);
        setProgress(100);
        setResult({
          accepted: res.accepted,
          errors: res.errors,
          persisted: res.persisted,
        } as any);
        setStep(3);
        if (res.accepted > 0) {
          toast.success("CSV import persisted", { description: `${res.accepted} student records added to database.` });
        }
        return;
      } catch (err: unknown) {
        toast.error("Upload failed", { description: err instanceof Error ? err.message : "Failed to process upload." });
      }
    }
    let p = 0;
    const t = setInterval(() => {
      p += 12; setProgress(Math.min(p, 100));
      if (p >= 100) { clearInterval(t); setResult(validateRows(rows, mapping)); setStep(3); }
    }, 120);
  };

  const missingRequired = ["student_name", "apaar_id", "programme_code"].filter((k) => (mapping[k] ?? -1) < 0);

  return (
    <>
      <PageHeader crumbs={[{ label: "Student Records" }, { label: "CSV Imports" }]} title="CSV imports" description="Import student records in bulk. Rows are validated before anything is sent for saving."
        actions={<Button variant="outline" onClick={() => downloadCsv("apaar_import_template.csv", [TEMPLATE_HEADERS, ["Example Student", "123456789012", "BT-CSE", "2026-27", "General", "Admitted", "2006-04-12"]])}><Download className="size-4" /> Download template</Button>} />

      <ol className="mb-6 grid grid-cols-4 gap-2" aria-label="Import progress">
        {STEPS.map((s, i) => (
          <li key={s} aria-current={i === step ? "step" : undefined} className={cn("border-t-2 pt-3 text-xs", i < step ? "border-teal text-teal" : i === step ? "border-primary font-semibold text-foreground" : "border-border text-muted-foreground")}>
            <span className="tabular-nums">0{i + 1}</span> <span className="hidden sm:inline">· {s}</span>
          </li>
        ))}
      </ol>

      <div className="rounded-md border bg-surface p-6 shadow-subtle">
        {step === 0 && (
          <>
            <div onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={onDrop}
              className={cn("flex flex-col items-center rounded-md border-2 border-dashed px-6 py-14 text-center transition-colors", drag ? "border-primary bg-info-soft" : "border-input")}>
              <Upload className="mb-3 size-7 text-muted-foreground" />
              <p className="text-sm font-medium">Drag and drop a CSV file here</p>
              <p className="mt-1 text-xs text-muted-foreground">UTF-8 encoded, first row must contain headers.</p>
              <Button variant="outline" size="sm" className="mt-4" onClick={() => input.current?.click()}>Choose file</Button>
              <input ref={input} type="file" accept=".csv,text/csv" className="sr-only" onChange={(e) => e.target.files?.[0] && accept(e.target.files[0])} />
            </div>
            {error && <p role="alert" className="mt-4 flex items-center gap-2 rounded-sm bg-error-soft px-3 py-2 text-sm text-destructive"><AlertTriangle className="size-4" />{error}</p>}
          </>
        )}

        {step === 1 && (
          <>
            <div className="mb-5 flex items-center gap-3 text-sm"><FileText className="size-4 text-muted-foreground" /><span className="font-medium">{file?.name}</span><span className="text-muted-foreground">· {rows.length} rows · {headers.length} columns detected</span></div>
            <table className="w-full">
              <thead className="bg-muted/50"><tr><th className={th}>Template field</th><th className={th}>Column in your file</th></tr></thead>
              <tbody>{TEMPLATE_HEADERS.map((t) => (
                <tr key={t} className="border-t"><td className={`${td} font-mono text-xs`}>{t}</td><td className={td}>
                  <Select value={String(mapping[t] ?? -1)} onValueChange={(v) => setMapping({ ...mapping, [t]: Number(v) })}>
                    <SelectTrigger className="w-64" aria-label={`Map ${t}`}><SelectValue /></SelectTrigger>
                    <SelectContent><SelectItem value="-1">— Not mapped —</SelectItem>{headers.map((h, i) => <SelectItem key={i} value={String(i)}>{h}</SelectItem>)}</SelectContent>
                  </Select>
                </td></tr>
              ))}</tbody>
            </table>
            {missingRequired.length > 0 && <p className="mt-4 text-xs text-warning">Required fields not mapped: {missingRequired.join(", ")}</p>}
            <div className="mt-6 flex justify-between"><Button variant="outline" onClick={reset}>Back</Button><Button disabled={missingRequired.length > 0} onClick={runValidation}>Validate records</Button></div>
          </>
        )}

        {step === 2 && (
          <div className="py-10 text-center">
            <Loader2 className="mx-auto mb-4 size-6 animate-spin text-primary" />
            <p className="text-sm font-medium">Validating {rows.length} rows…</p>
            <Progress value={progress} className="mx-auto mt-4 max-w-md" />
          </div>
        )}

        {step === 3 && result && (
          <>
            <div className="grid grid-cols-3 divide-x rounded-md border">
              <div className="p-4"><div className="text-xs text-muted-foreground">Rows checked</div><div className="font-display text-2xl font-semibold">{rows.length}</div></div>
              <div className="p-4"><div className="text-xs text-muted-foreground">Passed validation</div><div className="font-display text-2xl font-semibold text-success">{result.accepted}</div></div>
              <div className="p-4"><div className="text-xs text-muted-foreground">Rejected</div><div className="font-display text-2xl font-semibold text-destructive">{rows.length - result.accepted}</div></div>
            </div>
            {(result as any).persisted ? (
              <div className="mt-4 rounded-sm border border-success/40 bg-success-soft px-4 py-3 text-xs text-success">
                Validation confirmed and persisted by backend API. <strong>{result.accepted}</strong> valid student records have been saved to the database.
              </div>
            ) : (
              <div className="mt-4 rounded-sm border border-warning/40 bg-warning-soft px-4 py-3 text-xs text-warning">
                Validation ran in your browser. Rows are <strong>not saved</strong> — persistence requires backend confirmation.
              </div>
            )}
            {result.errors.length > 0 ? (
              <div className="mt-6">
                <div className="mb-2 flex items-center justify-between"><h3 className="text-sm font-semibold">Row-level errors</h3>
                  <Button variant="outline" size="sm" onClick={() => downloadCsv(`${file?.name ?? "import"}_errors.csv`, [["row", "field", "value", "rule"], ...result.errors.map((e) => [e.row, e.field, e.value, e.rule])])}><Download className="size-4" /> Error report</Button></div>
                <div className="max-h-80 overflow-auto rounded-md border">
                  <table className="w-full"><thead className="sticky top-0 bg-muted"><tr><th className={th}>Row</th><th className={th}>Field</th><th className={th}>Value</th><th className={th}>Rule</th></tr></thead>
                    <tbody>{result.errors.map((e, i) => <tr key={i} className={tr}><td className={`${td} tabular-nums`}>{e.row}</td><td className={`${td} font-mono text-xs`}>{e.field}</td><td className={`${td} font-mono text-xs`}>{e.value || "—"}</td><td className={`${td} text-muted-foreground`}>{e.rule}</td></tr>)}</tbody></table>
                </div>
              </div>
            ) : <p className="mt-6 flex items-center gap-2 text-sm text-success"><Check className="size-4" /> All rows passed validation.</p>}
            <div className="mt-6 flex justify-end"><Button onClick={reset}>Start a new import</Button></div>
          </>
        )}
      </div>

      <Section title="Import history" className="mt-8">
        <div className="overflow-x-auto"><table className="w-full min-w-[700px]">
          <thead><tr><th className={th}>Batch</th><th className={th}>File</th><th className={th}>Uploaded</th><th className={`${th} text-right`}>Accepted</th><th className={`${th} text-right`}>Rejected</th><th className={th}>Status</th></tr></thead>
          <tbody>{batches.map((b) => (
            <tr key={b.id} className={tr}><td className={td}><Link to="/uploads/$batchId" params={{ batchId: b.id }} className="font-medium text-primary hover:underline">{b.id}</Link></td><td className={td}>{b.file}</td><td className={`${td} text-muted-foreground`}>{b.uploadedBy} · {fmtDate(b.at, true)}</td><td className={`${td} text-right tabular-nums`}>{b.accepted}</td><td className={`${td} text-right tabular-nums`}>{b.rejected}</td><td className={td}><StatusBadge value={b.status} /></td></tr>
          ))}</tbody>
        </table></div>
      </Section>
    </>
  );
}
