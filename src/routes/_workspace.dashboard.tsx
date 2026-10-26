import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { useEffect, useState } from "react";
import { FileUp, FileBarChart, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader, Section, StatusBadge, fmtDate, th, td, tr } from "@/components/app/primitives";
import { studentsQuery, programmesQuery, findingsQuery, importsQuery, auditQuery } from "@/lib/services";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/dashboard")({
  head: pageHead("Dashboard", "Institutional overview of student records, enrolment against approved intake, imports and validation findings."),
  loader: ({ context: { queryClient: q } }) =>
    Promise.all([q.ensureQueryData(studentsQuery()), q.ensureQueryData(programmesQuery()), q.ensureQueryData(findingsQuery()), q.ensureQueryData(importsQuery()), q.ensureQueryData(auditQuery())]),
  component: Dashboard,
});

function Dashboard() {
  const { data: students } = useSuspenseQuery(studentsQuery());
  const { data: programmes } = useSuspenseQuery(programmesQuery());
  const { data: findings } = useSuspenseQuery(findingsQuery());
  const { data: imports } = useSuspenseQuery(importsQuery());
  const { data: audit } = useSuspenseQuery(auditQuery());

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const enrol = programmes.reduce((a, p) => a + p.actualEnrolment, 0);
  const intake = programmes.reduce((a, p) => a + p.approvedIntake, 0);
  const review = students.filter((s) => s.status !== "Verified").length;
  const statusCounts = Object.entries(students.reduce<Record<string, number>>((a, s) => ((a[s.status] = (a[s.status] ?? 0) + 1), a), {}));
  const attention = findings.filter((f) => f.status === "Open" || f.status === "Escalated").slice(0, 5);

  const metrics = [
    { label: "Total student records", value: students.length, note: "Across all programmes" },
    { label: "Actual enrolment", value: enrol, note: "Academic year 2026–27" },
    { label: "Approved intake", value: intake, note: "Per intake configuration" },
    { label: "Records requiring review", value: review, note: `${Math.round((review / students.length) * 100)}% of records`, tone: "text-warning" },
  ];

  return (
    <>
      <PageHeader
        crumbs={[{ label: "Overview" }, { label: "Dashboard" }]}
        title="Institutional dashboard"
        description="Demo Institute of Technology · All figures below are synthetic demo values."
        actions={<>
          <Button variant="outline" asChild><Link to="/reports"><FileBarChart className="size-4" /> Generate report</Link></Button>
          <Button asChild><Link to="/uploads"><FileUp className="size-4" /> Import student data</Link></Button>
        </>}
      />

      <div className="grid grid-cols-2 divide-x divide-y rounded-md border bg-surface shadow-subtle lg:grid-cols-4 lg:divide-y-0">
        {metrics.map((m) => (
          <div key={m.label} className="p-5">
            <div className="text-xs text-muted-foreground">{m.label}</div>
            <div className={`mt-2 font-display text-3xl font-semibold tabular-nums ${m.tone ?? ""}`}>{m.value.toLocaleString("en-IN")}</div>
            <div className="mt-1 text-[11px] text-muted-foreground">{m.note}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Section title="Enrolment versus approved intake" description="By programme, current academic year" className="xl:col-span-2">
          <div className="h-72 p-4">
            {mounted && <ResponsiveContainer width="100%" height="100%">
              <BarChart data={programmes} barGap={2}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="code" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} width={36} />
                <Tooltip cursor={{ fill: "var(--muted)" }} contentStyle={{ borderRadius: 6, border: "1px solid var(--border)", fontSize: 12 }} />
                <Legend iconType="square" wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="approvedIntake" name="Approved intake" fill="var(--chart-5)" radius={[2, 2, 0, 0]} />
                <Bar dataKey="actualEnrolment" name="Actual enrolment" fill="var(--chart-1)" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>}
          </div>
        </Section>

        <Section title="Record status distribution" description={`${students.length} records`}>
          <ul className="space-y-4 p-5">
            {statusCounts.map(([s, n]) => (
              <li key={s}>
                <div className="mb-1.5 flex justify-between text-xs"><StatusBadge value={s} /><span className="tabular-nums text-muted-foreground">{n}</span></div>
                <div className="h-1.5 rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${(n / students.length) * 100}%` }} /></div>
              </li>
            ))}
          </ul>
        </Section>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Section title="Recent CSV imports" actions={<Link to="/uploads" className="text-xs font-medium text-primary hover:underline">View all</Link>}>
          <table className="w-full">
            <thead><tr><th className={th}>File</th><th className={th}>Rows</th><th className={th}>Status</th></tr></thead>
            <tbody>
              {imports.slice(0, 4).map((b) => (
                <tr key={b.id} className={tr}>
                  <td className={td}><Link to="/uploads/$batchId" params={{ batchId: b.id }} className="font-medium hover:text-primary">{b.file}</Link><div className="text-xs text-muted-foreground">{b.id} · {fmtDate(b.at)}</div></td>
                  <td className={`${td} tabular-nums`}>{b.accepted}/{b.total}</td>
                  <td className={td}><StatusBadge value={b.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        <Section title="Validation findings requiring attention" actions={<Link to="/findings" className="text-xs font-medium text-primary hover:underline">Review queue</Link>}>
          <ul>
            {attention.map((f) => (
              <li key={f.id} className={tr}>
                <Link to="/findings/$id" params={{ id: f.id }} className="flex items-center gap-4 px-5 py-3">
                  <StatusBadge value={f.severity} />
                  <div className="min-w-0 flex-1"><div className="truncate text-sm font-medium">{f.category}</div><div className="text-xs text-muted-foreground">{f.id} · {f.studentId}</div></div>
                  <StatusBadge value={f.status} /><ArrowRight className="size-4 text-muted-foreground" />
                </Link>
              </li>
            ))}
          </ul>
        </Section>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Section title="Programme-level enrolment" className="xl:col-span-2">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr><th className={th}>Programme</th><th className={`${th} text-right`}>Intake</th><th className={`${th} text-right`}>Enrolled</th><th className={th}>Utilisation</th></tr></thead>
              <tbody>
                {programmes.map((p) => {
                  const u = Math.round((p.actualEnrolment / p.approvedIntake) * 100);
                  return (
                    <tr key={p.code} className={tr}>
                      <td className={td}><div className="font-medium">{p.name}</div><div className="text-xs text-muted-foreground">{p.code}</div></td>
                      <td className={`${td} text-right tabular-nums`}>{p.approvedIntake}</td>
                      <td className={`${td} text-right tabular-nums`}>{p.actualEnrolment}</td>
                      <td className={td}><div className="flex items-center gap-2"><div className="h-1.5 w-24 rounded-full bg-muted"><div className={`h-full rounded-full ${u > 100 ? "bg-destructive" : "bg-teal"}`} style={{ width: `${Math.min(u, 100)}%` }} /></div><span className={`text-xs tabular-nums ${u > 100 ? "font-semibold text-destructive" : ""}`}>{u}%</span></div></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Section>
        <Section title="Recent administrative activity">
          <ol className="space-y-4 p-5">
            {audit.slice(0, 6).map((a) => (
              <li key={a.id} className="flex gap-3 text-sm">
                <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
                <div><div>{a.actor} <span className="text-muted-foreground">· {a.action.toLowerCase()}</span></div><div className="text-xs text-muted-foreground">{fmtDate(a.at, true)} · {a.ref}</div></div>
              </li>
            ))}
          </ol>
        </Section>
      </div>
    </>
  );
}
