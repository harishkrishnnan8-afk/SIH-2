import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Search } from "lucide-react";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { PageHeader, StatusBadge, EmptyState, th, td, tr } from "@/components/app/primitives";
import { institutionsQuery } from "@/lib/services";
import { centralInstitutions, type Institution } from "@/lib/demo/data";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/institutions")({
  head: pageHead("Institutions", "Institutions within your access scope, with status, programme and student counts."),
  loader: ({ context }) => context.queryClient.ensureQueryData(institutionsQuery()),
  component: Institutions,
});

function Institutions() {
  const { data } = useSuspenseQuery(institutionsQuery());
  const [q, setQ] = useState("");
  const [edit, setEdit] = useState<Institution | null>(null);
  const rows = data.filter((i) => !q || i.name.toLowerCase().includes(q.toLowerCase()) || i.ref.toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <PageHeader crumbs={[{ label: "Institutions" }]} title="Institutions" description="Fictional demo institutions. References are internal and not official AICTE codes." />
      <div className="relative mb-4 max-w-sm"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search name or reference" className="bg-surface pl-9" aria-label="Search institutions" /></div>
      <div className="overflow-x-auto rounded-md border bg-surface shadow-subtle">
        {rows.length === 0 ? <EmptyState title="No institutions found" body="Try another search term." /> : (
          <table className="w-full min-w-[760px]">
            <thead className="bg-muted/50"><tr><th className={th}>Institution</th><th className={th}>State</th><th className={th}>Status</th><th className={`${th} text-right`}>Programmes</th><th className={`${th} text-right`}>Students</th><th className={th} /></tr></thead>
            <tbody>{rows.map((i, n) => (
              <tr key={i.id} className={tr}><td className={td}><div className="font-medium">{i.name}</div><div className="font-mono text-xs text-muted-foreground">{i.ref}</div></td><td className={td}>{i.state}</td><td className={td}><StatusBadge value={i.status} /></td><td className={`${td} text-right tabular-nums`}>{[6, 14, 4, 5, 9][n] ?? 0}</td><td className={`${td} text-right tabular-nums`}>{centralInstitutions[n]?.enrolment ?? 0}</td><td className={`${td} text-right`}><Button variant="ghost" size="sm" onClick={() => setEdit(i)}>Edit</Button></td></tr>
            ))}</tbody>
          </table>
        )}
      </div>
      <Sheet open={!!edit} onOpenChange={(o) => !o && setEdit(null)}>
        <SheetContent>
          <SheetHeader><SheetTitle>Edit institution</SheetTitle><SheetDescription>{edit?.ref}</SheetDescription></SheetHeader>
          <form className="space-y-4 px-4" onSubmit={(e) => { e.preventDefault(); toast.warning("Not saved — backend not connected"); setEdit(null); }}>
            <div className="space-y-1.5"><Label htmlFor="iname">Name</Label><Input id="iname" defaultValue={edit?.name} /></div>
            <div className="space-y-1.5"><Label htmlFor="istate">State</Label><Input id="istate" defaultValue={edit?.state} /></div>
            <Button type="submit" className="w-full">Save changes</Button>
          </form>
        </SheetContent>
      </Sheet>
    </>
  );
}
