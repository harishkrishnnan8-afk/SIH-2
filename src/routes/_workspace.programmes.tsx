import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageHeader, StatusBadge, th, td, tr } from "@/components/app/primitives";
import { programmesQuery } from "@/lib/services";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/programmes")({
  head: pageHead("Programmes", "Programmes with approved intake, actual enrolment and intake policy configuration."),
  loader: ({ context }) => context.queryClient.ensureQueryData(programmesQuery()),
  component: Programmes,
});

function Programmes() {
  const { data } = useSuspenseQuery(programmesQuery());
  const [q, setQ] = useState("");
  const rows = data.filter((p) => !q || `${p.name} ${p.code}`.toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <PageHeader crumbs={[{ label: "Institutions" }, { label: "Programmes" }]} title="Programmes" description="Demo Institute of Technology · Academic year 2026–27" />
      <div className="relative mb-4 max-w-sm"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search programme or code" className="bg-surface pl-9" aria-label="Search programmes" /></div>
      <div className="overflow-x-auto rounded-md border bg-surface shadow-subtle">
        <table className="w-full min-w-[820px]">
          <thead className="bg-muted/50"><tr><th className={th}>Programme</th><th className={th}>Code</th><th className={th}>Year</th><th className={`${th} text-right`}>Approved intake</th><th className={`${th} text-right`}>Actual enrolment</th><th className={th}>Intake policy</th></tr></thead>
          <tbody>{rows.map((p) => (
            <tr key={p.code} className={tr}><td className={`${td} font-medium`}>{p.name}</td><td className={`${td} font-mono text-xs`}>{p.code}</td><td className={td}>{p.year}</td><td className={`${td} text-right tabular-nums`}>{p.approvedIntake}</td><td className={`${td} text-right tabular-nums ${p.actualEnrolment > p.approvedIntake ? "font-semibold text-destructive" : ""}`}>{p.actualEnrolment}</td><td className={td}><StatusBadge value={p.policy} tone={p.policy.startsWith("Pending") ? "warning" : "neutral"} /></td></tr>
          ))}</tbody>
        </table>
      </div>
    </>
  );
}
