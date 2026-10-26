import { createFileRoute } from "@tanstack/react-router";
import { Lock } from "lucide-react";
import { PageHeader, Section, StatusBadge, th, td, tr } from "@/components/app/primitives";
import { centralInstitutions } from "@/lib/demo/data";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/central")({
  head: pageHead("Central review", "Aggregated enrolment, intake utilisation, findings and data quality across institutions for central reviewers."),
  component: Central,
});

function Central() {
  const d = centralInstitutions;
  const enrol = d.reduce((a, x) => a + x.enrolment, 0);
  const intake = d.reduce((a, x) => a + x.intake, 0);
  const metrics = [
    ["Institutions in scope", d.length],
    ["Total enrolment", enrol.toLocaleString("en-IN")],
    ["Intake utilisation", `${Math.round((enrol / intake) * 100)}%`],
    ["Outstanding findings", d.reduce((a, x) => a + x.findings, 0)],
  ];
  return (
    <>
      <PageHeader crumbs={[{ label: "Overview" }, { label: "Central Review" }]} title="Central reviewer dashboard" description="Aggregates across institutions in your permission scope. Synthetic demo values."
        actions={<span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground"><Lock className="size-3.5" /> Scope: All demo institutions</span>} />
      <div className="mb-6 grid grid-cols-2 divide-x divide-y rounded-md border bg-surface shadow-subtle lg:grid-cols-4 lg:divide-y-0">
        {metrics.map(([l, v]) => <div key={l} className="p-5"><div className="text-xs text-muted-foreground">{l}</div><div className="mt-2 font-display text-3xl font-semibold tabular-nums">{v}</div></div>)}
      </div>
      <Section title="Institutions">
        <div className="overflow-x-auto"><table className="w-full min-w-[880px]">
          <thead><tr><th className={th}>Institution</th><th className={`${th} text-right`}>Enrolment</th><th className={th}>Utilisation</th><th className={`${th} text-right`}>Findings</th><th className={th}>Submission</th><th className={th}>Data quality</th></tr></thead>
          <tbody>{d.map((x) => {
            const u = Math.round((x.enrolment / x.intake) * 100);
            return (
              <tr key={x.id} className={tr}>
                <td className={td}><div className="font-medium">{x.name}</div><div className="font-mono text-xs text-muted-foreground">{x.ref}</div></td>
                <td className={`${td} text-right tabular-nums`}>{x.enrolment}</td>
                <td className={`${td} tabular-nums`}>{u}%</td>
                <td className={`${td} text-right tabular-nums`}>{x.findings}</td>
                <td className={td}><StatusBadge value={x.submission} /></td>
                <td className={td}><div className="flex items-center gap-2"><div className="h-1.5 w-20 rounded-full bg-muted"><div className={`h-full rounded-full ${x.quality < 80 ? "bg-warning" : "bg-success"}`} style={{ width: `${x.quality}%` }} /></div><span className="text-xs tabular-nums">{x.quality}</span></div></td>
              </tr>
            );
          })}</tbody>
        </table></div>
      </Section>
    </>
  );
}
