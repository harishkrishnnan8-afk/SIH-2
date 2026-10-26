import { createFileRoute } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Loader2, Search, CheckCircle2, XCircle, MinusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader, Section, SimulatedBanner, StatusBadge, fmtDate, th, td, tr } from "@/components/app/primitives";
import { verifyApaar, type VerificationResult } from "@/lib/services";
import { maskApaar } from "@/lib/api/client";
import { students } from "@/lib/demo/data";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/verification")({
  head: pageHead("Verification", "Look up APAAR identifiers and run format, internal and provider verification checks."),
  component: Verification,
});

function Check({ label, kind, ok, note }: { label: string; kind: string; ok: boolean | null; note: string }) {
  const Icon = ok === null ? MinusCircle : ok ? CheckCircle2 : XCircle;
  return (
    <div className="flex gap-3 p-5">
      <Icon className={`mt-0.5 size-5 shrink-0 ${ok === null ? "text-muted-foreground" : ok ? "text-success" : "text-destructive"}`} />
      <div><div className="text-sm font-medium">{label} <span className="ml-1 eyebrow text-muted-foreground">{kind}</span></div><p className="text-xs text-muted-foreground">{note}</p></div>
    </div>
  );
}

function Verification() {
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState<VerificationResult | null>(null);
  const [log, setLog] = useState<{ id: string; at: string; result: string }[]>([]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const r = await verifyApaar(value);
    setRes(r); setLoading(false);
    setLog((l) => [{ id: maskApaar(value), at: r.checkedAt, result: r.formatValid && r.internalMatch ? "Matched (simulated)" : "No match" }, ...l]);
  };

  return (
    <>
      <PageHeader crumbs={[{ label: "Verification & Reporting" }, { label: "Verification" }]} title="Verification" description="Each check type is labelled separately. External verification is not connected." />
      <SimulatedBanner />
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Section title="Record lookup">
            <form onSubmit={submit} className="flex flex-wrap items-end gap-3 p-5">
              <div className="min-w-64 flex-1 space-y-1.5"><Label htmlFor="apaar">APAAR identifier</Label><Input id="apaar" value={value} onChange={(e) => setValue(e.target.value)} inputMode="numeric" className="font-mono" placeholder="12-digit identifier" /></div>
              <Button type="submit" disabled={loading || !value}>{loading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />} Verify</Button>
            </form>
            <p className="border-t px-5 py-3 text-xs text-muted-foreground">Try a demo identifier: <button type="button" className="font-mono text-primary hover:underline" onClick={() => setValue(students[0]?.apaar ?? "")}>{maskApaar(students[0]?.apaar ?? "")}</button> (fills the field)</p>
          </Section>
          {res && (
            <Section title="Result" description={`Checked ${fmtDate(res.checkedAt, true)}`} actions={<StatusBadge value={`Provider: ${res.providerStatus}`} tone="warning" />}>
              <div className="divide-y">
                <Check label="Format check" kind="Local" ok={res.formatValid} note="Identifier contains exactly 12 digits." />
                <Check label="Internal record check" kind="Institution records" ok={res.internalMatch} note={res.student ? `Matches ${res.student.id} · ${res.student.name}` : "No record in this institution uses this identifier."} />
                <Check label="Simulated verification" kind="Mock provider" ok={res.formatValid && res.internalMatch} note="Simulated response. Not an official APAAR verification." />
                <Check label="External APAAR verification" kind="Official" ok={null} note="Not connected. No external request was made." />
              </div>
            </Section>
          )}
        </div>
        <Section title="Verification history" description="This session">
          {log.length === 0 ? <p className="p-5 text-sm text-muted-foreground">No checks yet.</p> : (
            <table className="w-full"><thead><tr><th className={th}>Identifier</th><th className={th}>Result</th></tr></thead>
              <tbody>{log.map((l, i) => <tr key={i} className={tr}><td className={`${td} font-mono text-xs`}>{l.id}<div className="font-sans text-muted-foreground">{fmtDate(l.at, true)}</div></td><td className={`${td} text-xs`}>{l.result}</td></tr>)}</tbody></table>
          )}
        </Section>
      </div>
    </>
  );
}
