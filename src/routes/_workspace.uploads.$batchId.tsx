import { createFileRoute, notFound } from "@tanstack/react-router";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader, Section, StatusBadge, fmtDate, th, td, tr } from "@/components/app/primitives";
import { imports, type ImportBatch } from "@/lib/demo/data";
import { downloadCsv } from "@/lib/csv";

export const Route = createFileRoute("/_workspace/uploads/$batchId")({
  head: ({ params }) => ({
    meta: [
      { title: `Import ${params.batchId} · APAAR Student Data Platform` },
      { name: "description", content: "CSV import batch summary with accepted and rejected rows." },
      { property: "og:title", content: `Import ${params.batchId} · APAAR` },
      { property: "og:description", content: "CSV import batch summary." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  loader: ({ params }) => {
    const b = imports.find((x) => x.id === params.batchId);
    if (!b) throw notFound();
    return b as (typeof imports)[number];
  },
  component: Batch,
});

const rules = ["APAAR identifier must be 12 digits.", "Programme code is required.", "Identifier repeated within this file.", "Category must be a configured admission category."];

function Batch() {
  const b = Route.useLoaderData() as ImportBatch;
  const errs = Array.from({ length: b.rejected }, (_, i) => ({ row: 4 + i * 7, field: ["apaar_id", "programme_code", "apaar_id", "admission_category"][i % 4] ?? "", rule: rules[i % 4] ?? "" }));
  return (
    <>
      <PageHeader crumbs={[{ label: "CSV Imports", to: "/uploads" }, { label: b.id }]} title={b.file} description={`Uploaded by ${b.uploadedBy} on ${fmtDate(b.at, true)}`}
        actions={<><StatusBadge value={b.status} />{b.rejected > 0 && <Button variant="outline" onClick={() => downloadCsv(`${b.id}_errors.csv`, [["row", "field", "rule"], ...errs.map((e) => [e.row, e.field, e.rule])])}><Download className="size-4" /> Error report</Button>}</>} />
      <div className="mb-6 grid grid-cols-3 divide-x rounded-md border bg-surface">
        {[["Total rows", b.total, ""], ["Accepted", b.accepted, "text-success"], ["Rejected", b.rejected, "text-destructive"]].map(([l, v, c]) => (
          <div key={l as string} className="p-5"><div className="text-xs text-muted-foreground">{l}</div><div className={`font-display text-3xl font-semibold ${c}`}>{v}</div></div>
        ))}
      </div>
      <Section title="Rejected rows" description="Demo summary — row details are synthetic.">
        {errs.length === 0 ? <p className="p-5 text-sm text-muted-foreground">No rows were rejected.</p> : (
          <table className="w-full"><thead><tr><th className={th}>Row</th><th className={th}>Field</th><th className={th}>Rule</th></tr></thead>
            <tbody>{errs.map((e) => <tr key={e.row} className={tr}><td className={td}>{e.row}</td><td className={`${td} font-mono text-xs`}>{e.field}</td><td className={`${td} text-muted-foreground`}>{e.rule}</td></tr>)}</tbody></table>
        )}
      </Section>
    </>
  );
}
