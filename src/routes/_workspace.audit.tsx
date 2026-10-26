import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Lock, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageHeader, StatusBadge, fmtDate, th, td, tr } from "@/components/app/primitives";
import { auditQuery } from "@/lib/services";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/audit")({
  head: pageHead("Audit trail", "Read-only record of administrative actions, actors, roles and results."),
  loader: ({ context }) => context.queryClient.ensureQueryData(auditQuery()),
  component: Audit,
});

function Audit() {
  const { data } = useSuspenseQuery(auditQuery());
  const [q, setQ] = useState("");
  const rows = data.filter((a) => !q || `${a.actor} ${a.action} ${a.ref}`.toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <PageHeader crumbs={[{ label: "Governance" }, { label: "Audit Trail" }]} title="Audit trail" description="Entries are generated from backend events and cannot be edited. Sensitive identifiers are never shown here."
        actions={<span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground"><Lock className="size-3.5" /> Read-only</span>} />
      <div className="relative mb-4 max-w-sm"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by actor, action or reference" className="bg-surface pl-9" aria-label="Filter audit" /></div>
      <div className="overflow-x-auto rounded-md border bg-surface shadow-subtle">
        <table className="w-full min-w-[820px]">
          <thead className="bg-muted/50"><tr><th className={th}>Timestamp</th><th className={th}>Actor</th><th className={th}>Role</th><th className={th}>Action</th><th className={th}>Record reference</th><th className={th}>Result</th></tr></thead>
          <tbody>{rows.map((a) => (
            <tr key={a.id} className={tr}><td className={`${td} whitespace-nowrap font-mono text-xs text-muted-foreground`}>{fmtDate(a.at, true)}</td><td className={td}>{a.actor}</td><td className={`${td} text-muted-foreground`}>{a.role}</td><td className={td}>{a.action}</td><td className={`${td} font-mono text-xs`}>{a.ref}</td><td className={td}><StatusBadge value={a.result} /></td></tr>
          ))}</tbody>
        </table>
      </div>
    </>
  );
}
