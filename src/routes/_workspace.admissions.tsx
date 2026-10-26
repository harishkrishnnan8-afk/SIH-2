import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { PageHeader, Section, StatusBadge, th, td, tr } from "@/components/app/primitives";
import { studentsQuery } from "@/lib/services";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/admissions")({
  head: pageHead("Admissions", "Admission records by category for the current academic year, kept separate from student identity."),
  loader: ({ context }) => context.queryClient.ensureQueryData(studentsQuery()),
  component: Admissions,
});

function Admissions() {
  const { data } = useSuspenseQuery(studentsQuery());
  const cats = ["General", "Supernumerary", "NRI", "OCI", "Foreign National"].map((c) => ({ c, n: data.filter((s) => s.category === c).length }));
  return (
    <>
      <PageHeader crumbs={[{ label: "Student Records" }, { label: "Admissions" }]} title="Admissions" description="Admission records for academic year 2026–27. Each admission links to a student identity record." />
      <div className="mb-6 grid grid-cols-2 divide-x divide-y rounded-md border bg-surface sm:grid-cols-5 sm:divide-y-0">
        {cats.map(({ c, n }) => <div key={c} className="p-4"><div className="text-xs text-muted-foreground">{c}</div><div className="font-display text-2xl font-semibold tabular-nums">{n}</div></div>)}
      </div>
      <Section title="Admission records">
        <div className="overflow-x-auto"><table className="w-full min-w-[720px]">
          <thead><tr><th className={th}>Admission ref</th><th className={th}>Student</th><th className={th}>Programme</th><th className={th}>Category</th><th className={th}>Year</th><th className={th}>Record status</th></tr></thead>
          <tbody>{data.slice(0, 20).map((s) => (
            <tr key={s.id} className={tr}><td className={`${td} font-mono text-xs`}>ADM-{s.id.slice(4)}-{s.admissionYear}</td><td className={td}><Link to="/students/$id" params={{ id: s.id }} className="hover:text-primary">{s.name}</Link></td><td className={td}>{s.programme}</td><td className={td}>{s.category}</td><td className={td}>{s.admissionYear}</td><td className={td}><StatusBadge value={s.status} /></td></tr>
          ))}</tbody>
        </table></div>
      </Section>
    </>
  );
}
