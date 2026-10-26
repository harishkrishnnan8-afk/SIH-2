import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader, Section, fmtDate, th, td, tr } from "@/components/app/primitives";
import { programmes } from "@/lib/demo/data";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/intake-configuration")({
  head: pageHead("Intake configuration", "Configure approved intake and treatment of supernumerary, NRI, OCI and foreign national seats."),
  component: Intake,
});

const RULES = [
  { key: "supernumerary", label: "Supernumerary seats", desc: "Whether supernumerary admissions count towards approved intake utilisation." },
  { key: "nri", label: "NRI category", desc: "How NRI admissions are treated in intake utilisation." },
  { key: "oci", label: "OCI status", desc: "How OCI admissions are treated in intake utilisation." },
  { key: "foreign", label: "Foreign nationals", desc: "How foreign national admissions are treated in intake utilisation." },
];
const OPTIONS = ["Counted within intake", "Counted separately", "Excluded from utilisation", "Not yet configured"];

function Intake() {
  const [vals, setVals] = useState<Record<string, string>>({ supernumerary: "Counted separately", nri: "Not yet configured", oci: "Not yet configured", foreign: "Not yet configured" });
  const [history, setHistory] = useState([
    { at: "2026-10-12T10:20:00Z", who: "P. Nair", what: "Approved intake for BT-CSE set to 180" },
    { at: "2026-10-02T09:00:00Z", who: "P. Nair", what: "Supernumerary seats → Counted separately" },
  ]);
  const save = () => {
    setHistory((h) => [{ at: new Date().toISOString(), who: "Priya Nair", what: "Configuration updated (not persisted)" }, ...h]);
    toast.warning("Not saved — backend not connected", { description: "Change listed in history for this session only." });
  };
  return (
    <>
      <PageHeader crumbs={[{ label: "Institutions" }, { label: "Intake Configuration" }]} title="Intake configuration" description="All rules here are configurable placeholders until authoritative regulatory requirements are confirmed." actions={<Button onClick={save}>Save configuration</Button>} />
      <div className="mb-6 flex gap-3 rounded-md border border-warning/40 bg-warning-soft p-4 text-sm text-warning"><AlertTriangle className="size-4 shrink-0" />This platform does not apply official regulatory calculations. Confirm each treatment with the Regulation Bureau before relying on utilisation figures.</div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Section title="Category treatment">
          <div className="divide-y">{RULES.map((r) => (
            <div key={r.key} className="grid gap-3 p-5 sm:grid-cols-[1fr_220px] sm:items-center">
              <div><Label htmlFor={r.key}>{r.label}</Label><p className="mt-0.5 text-xs text-muted-foreground">{r.desc}</p></div>
              <Select value={vals[r.key] ?? ""} onValueChange={(v) => setVals({ ...vals, [r.key]: v })}><SelectTrigger id={r.key}><SelectValue /></SelectTrigger><SelectContent>{OPTIONS.map((o) => <SelectItem key={o} value={o}>{o}</SelectItem>)}</SelectContent></Select>
            </div>
          ))}</div>
        </Section>
        <Section title="Approved intake by programme">
          <table className="w-full"><tbody>{programmes.map((p) => (
            <tr key={p.code} className={tr}><td className={td}><div className="font-medium">{p.code}</div><div className="text-xs text-muted-foreground">{p.name}</div></td><td className={`${td} w-32`}><Input type="number" min={0} defaultValue={p.approvedIntake} aria-label={`Approved intake for ${p.code}`} className="text-right tabular-nums" /></td></tr>
          ))}</tbody></table>
        </Section>
      </div>
      <Section title="Update history" className="mt-6">
        <table className="w-full"><thead><tr><th className={th}>When</th><th className={th}>By</th><th className={th}>Change</th></tr></thead>
          <tbody>{history.map((h, i) => <tr key={i} className={tr}><td className={`${td} text-muted-foreground`}>{fmtDate(h.at, true)}</td><td className={td}>{h.who}</td><td className={td}>{h.what}</td></tr>)}</tbody></table>
      </Section>
    </>
  );
}
