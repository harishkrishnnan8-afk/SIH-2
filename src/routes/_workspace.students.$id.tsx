import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Eye, EyeOff, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader, Section, StatusBadge, fmtDate, td, tr } from "@/components/app/primitives";
import { studentQuery } from "@/lib/services";
import { maskApaar } from "@/lib/api/client";
import { findings, programmes, audit } from "@/lib/demo/data";
import { toast } from "sonner";

export const Route = createFileRoute("/_workspace/students/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `Student ${params.id} · APAAR Student Data Platform` },
      { name: "description", content: "Student identity, admission, attributes, validation findings and review history." },
      { property: "og:title", content: `Student ${params.id} · APAAR` },
      { property: "og:description", content: "Student record detail view." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
      { name: "robots", content: "noindex" },
    ],
  }),
  loader: async ({ context, params }) => {
    const s = await context.queryClient.ensureQueryData(studentQuery(params.id));
    if (!s) throw notFound();
  },
  component: Detail,
});

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div><dt className="text-xs text-muted-foreground">{label}</dt><dd className="mt-1 text-sm font-medium">{children}</dd></div>;
}

function Detail() {
  const { id } = Route.useParams();
  const { data: s } = useSuspenseQuery(studentQuery(id));
  const [reveal, setReveal] = useState(false);
  if (!s) return null;
  const prog = programmes.find((p) => p.code === s.programme);
  const related = findings.filter((f) => f.studentId === s.id);
  const history = audit.slice(0, 4);

  return (
    <>
      <PageHeader
        crumbs={[{ label: "Students", to: "/students" }, { label: s.id }]}
        title={s.name}
        description={`${s.id} · ${prog?.name ?? s.programme}`}
        actions={<><StatusBadge value={s.status} /><Button variant="outline" asChild><Link to="/students/new"><Pencil className="size-4" /> Edit record</Link></Button></>}
      />
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Section title="Identity" description="Student identity is maintained separately from admission records.">
            <dl className="grid grid-cols-2 gap-6 p-5 md:grid-cols-3">
              <Field label="Full name">{s.name}</Field>
              <Field label="APAAR identifier">
                <span className="inline-flex items-center gap-2 font-mono">
                  {reveal ? s.apaar.replace(/(\d{4})(?=\d)/g, "$1 ") : maskApaar(s.apaar)}
                  <button onClick={() => { setReveal(!reveal); if (!reveal) toast("Identifier revealed", { description: "This view is recorded in the audit trail once the backend is connected." }); }} className="text-muted-foreground hover:text-foreground" aria-label={reveal ? "Hide identifier" : "Reveal identifier"}>
                    {reveal ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                  </button>
                </span>
              </Field>
              <Field label="Date of birth">{s.dob}</Field>
              <Field label="Gender">{s.gender}</Field>
              <Field label="Email">{s.email}</Field>
            </dl>
          </Section>
          <Section title="Admission">
            <dl className="grid grid-cols-2 gap-6 p-5 md:grid-cols-3">
              <Field label="Programme">{s.programme}</Field>
              <Field label="Admission year">{s.admissionYear}</Field>
              <Field label="Admission category">{s.category}</Field>
              <Field label="Admission status">Admitted</Field>
              <Field label="Academic year">2026–27</Field>
              <Field label="Last updated">{fmtDate(s.updated, true)}</Field>
            </dl>
          </Section>
          <Section title="Configurable attributes" description="Additional fields defined by the institution.">
            <dl className="grid grid-cols-2 gap-6 p-5 md:grid-cols-3">
              <Field label="NRI category">{s.category === "NRI" ? "Yes" : "No"}</Field>
              <Field label="OCI status">{s.category === "OCI" ? "Pending confirmation" : "Not applicable"}</Field>
              <Field label="Foreign national">{s.category === "Foreign National" ? "Yes" : "No"}</Field>
            </dl>
          </Section>
        </div>
        <div className="space-y-6">
          <Section title="Validation findings" description={`${related.length} linked`}>
            {related.length === 0 ? <p className="p-5 text-sm text-muted-foreground">No findings for this record.</p> : (
              <ul>{related.map((f) => <li key={f.id} className={tr}><Link to="/findings/$id" params={{ id: f.id }} className="flex items-center justify-between gap-2 px-5 py-3 text-sm"><span>{f.category}<span className="block text-xs text-muted-foreground">{f.id}</span></span><StatusBadge value={f.status} /></Link></li>)}</ul>
            )}
          </Section>
          <Section title="Review history">
            <table className="w-full"><tbody>{history.map((h) => <tr key={h.id} className={tr}><td className={td}><div>{h.action}</div><div className="text-xs text-muted-foreground">{h.actor} · {fmtDate(h.at, true)}</div></td></tr>)}</tbody></table>
          </Section>
        </div>
      </div>
    </>
  );
}
