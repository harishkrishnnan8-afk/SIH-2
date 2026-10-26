import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState } from "react";
import { PageHeader, StatusBadge, EmptyState, fmtDate, th, td, tr } from "@/components/app/primitives";
import { findingsQuery } from "@/lib/services";
import { cn } from "@/lib/utils";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/findings/")({
  head: pageHead("Validation findings", "Review queue of validation findings raised against student records."),
  loader: ({ context }) => context.queryClient.ensureQueryData(findingsQuery()),
  component: Findings,
});

const TABS = ["All", "Open", "Under review", "Resolved", "Escalated"] as const;

function Findings() {
  const { data } = useSuspenseQuery(findingsQuery());
  const [tab, setTab] = useState<(typeof TABS)[number]>("Open");
  const rows = data.filter((f) => tab === "All" || f.status === tab);
  return (
    <>
      <PageHeader crumbs={[{ label: "Student Records" }, { label: "Validation Findings" }]} title="Validation findings" description="Findings are automated signals for human review. A possible duplicate is not proof of fraud." />
      <div role="tablist" className="mb-4 flex gap-1 border-b">
        {TABS.map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={cn("-mb-px border-b-2 px-3 py-2 text-sm transition-colors", tab === t ? "border-primary font-medium text-foreground" : "border-transparent text-muted-foreground hover:text-foreground")}>
            {t} <span className="ml-1 text-xs tabular-nums text-muted-foreground">{t === "All" ? data.length : data.filter((f) => f.status === t).length}</span>
          </button>
        ))}
      </div>
      <div className="overflow-x-auto rounded-md border bg-surface shadow-subtle">
        {rows.length === 0 ? <EmptyState title="Queue is clear" body={`No findings with status “${tab}”.`} /> : (
          <table className="w-full min-w-[860px]">
            <thead className="bg-muted/50"><tr><th className={th}>Reference</th><th className={th}>Affected record</th><th className={th}>Category</th><th className={th}>Severity</th><th className={th}>Detected</th><th className={th}>Status</th><th className={th}>Reviewer</th></tr></thead>
            <tbody>{rows.map((f) => (
              <tr key={f.id} className={tr}>
                <td className={td}><Link to="/findings/$id" params={{ id: f.id }} className="font-medium text-primary hover:underline">{f.id}</Link></td>
                <td className={td}><Link to="/students/$id" params={{ id: f.studentId }} className="hover:text-primary">{f.studentId}</Link></td>
                <td className={td}>{f.category}</td>
                <td className={td}><StatusBadge value={f.severity} /></td>
                <td className={`${td} text-muted-foreground`}>{fmtDate(f.detected, true)}</td>
                <td className={td}><StatusBadge value={f.status} /></td>
                <td className={`${td} text-muted-foreground`}>{f.reviewer ?? "Unassigned"}</td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </div>
    </>
  );
}
