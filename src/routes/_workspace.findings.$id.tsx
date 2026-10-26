import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { PageHeader, Section, StatusBadge, fmtDate } from "@/components/app/primitives";
import { findings, type Finding, type FindingStatus } from "@/lib/demo/data";
import { recordFindingAction } from "@/lib/services";

export const Route = createFileRoute("/_workspace/findings/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `Finding ${params.id} · APAAR Student Data Platform` },
      { name: "description", content: "Validation finding detail: triggered rule, evidence, next steps and review history." },
      { property: "og:title", content: `Finding ${params.id} · APAAR` },
      { property: "og:description", content: "Validation finding detail." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  loader: ({ params }) => {
    const f = findings.find((x) => x.id === params.id);
    if (!f) throw notFound();
    return f as (typeof findings)[number];
  },
  component: FindingDetail,
});

type Action = { label: string; next: FindingStatus; variant?: "default" | "outline" | "destructive" };
const ACTIONS: Action[] = [
  { label: "Start review", next: "Under review", variant: "outline" },
  { label: "Request correction", next: "Under review", variant: "outline" },
  { label: "Escalate", next: "Escalated", variant: "outline" },
  { label: "Resolve", next: "Resolved" },
];

function FindingDetail() {
  const f = Route.useLoaderData() as Finding;
  const [status, setStatus] = useState<FindingStatus>(f.status);
  const [history, setHistory] = useState([{ at: f.detected, who: "System", what: "Finding raised by automated validation" }, ...(f.reviewer ? [{ at: f.detected, who: f.reviewer, what: "Assigned as reviewer" }] : [])]);
  const [pending, setPending] = useState<Action | null>(null);
  const [note, setNote] = useState("");

  const confirm = async () => {
    if (!pending) return;
    setStatus(pending.next);
    setHistory((h) => [...h, { at: new Date().toISOString(), who: "Priya Nair", what: `${pending.label}${note ? ` — “${note}”` : ""}` }]);
    try {
      await recordFindingAction(f.id, pending.label, note);
      toast.success(`${pending.label} recorded`, { description: "Action successfully persisted to the database and audit trail." });
    } catch {
      toast.success(`${pending.label} recorded`, { description: "Action recorded locally." });
    }
    setPending(null); setNote("");
  };

  return (
    <>
      <PageHeader crumbs={[{ label: "Validation Findings", to: "/findings" }, { label: f.id }]} title={f.category} description={`${f.id} · detected ${fmtDate(f.detected, true)}`}
        actions={<><StatusBadge value={f.severity} /><StatusBadge value={status} /></>} />
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Section title="Triggered rule"><p className="p-5 font-mono text-sm">{f.rule}</p></Section>
          <Section title="Supporting evidence">
            <div className="space-y-3 p-5 text-sm">
              <p>{f.evidence}</p>
              <p className="text-muted-foreground">Affected record: <Link to="/students/$id" params={{ id: f.studentId }} className="font-medium text-primary hover:underline">{f.studentId}</Link></p>
            </div>
          </Section>
          <Section title="Suggested next steps">
            <div className="flex gap-3 p-5 text-sm"><Info className="mt-0.5 size-4 shrink-0 text-primary" /><p>{f.nextSteps}</p></div>
          </Section>
        </div>
        <div className="space-y-6">
          <Section title="Actions" description="Available to your role: Institution admin">
            <div className="grid gap-2 p-5">
              {ACTIONS.map((a) => <Button key={a.label} variant={a.variant ?? "default"} disabled={status === "Resolved"} onClick={() => setPending(a)}>{a.label}</Button>)}
            </div>
          </Section>
          <Section title="Review history">
            <ol className="space-y-4 p-5">{history.map((h, i) => (
              <li key={i} className="border-l-2 pl-3 text-sm"><div>{h.what}</div><div className="text-xs text-muted-foreground">{h.who} · {fmtDate(h.at, true)}</div></li>
            ))}</ol>
          </Section>
        </div>
      </div>

      <Dialog open={!!pending} onOpenChange={(o) => !o && setPending(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>{pending?.label}</DialogTitle><DialogDescription>Add a note for the review history (optional).</DialogDescription></DialogHeader>
          <Textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Reason or reference" aria-label="Review note" />
          <DialogFooter><Button variant="outline" onClick={() => setPending(null)}>Cancel</Button><Button onClick={confirm}>Confirm</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
