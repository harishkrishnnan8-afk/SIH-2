import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ArrowUpDown, Plus, Search, ChevronLeft, ChevronRight, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader, StatusBadge, EmptyState, fmtDate, th, td, tr } from "@/components/app/primitives";
import { studentsQuery } from "@/lib/services";
import { maskApaar } from "@/lib/api/client";
import { programmes, type Student } from "@/lib/demo/data";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/students/")({
  head: pageHead("Students", "Search, filter and review student identity records with masked APAAR identifiers."),
  component: Students,
});

type SortKey = "name" | "programme" | "admissionYear" | "updated";
const PAGE = 12;

function Students() {
  const { data, isLoading, isError, refetch } = useQuery(studentsQuery());
  const [q, setQ] = useState("");
  const [prog, setProg] = useState("all");
  const [status, setStatus] = useState("all");
  const [sort, setSort] = useState<{ k: SortKey; dir: 1 | -1 }>({ k: "updated", dir: -1 });
  const [page, setPage] = useState(0);

  const rows = useMemo(() => {
    let r = (data ?? []).filter((s) => (prog === "all" || s.programme === prog) && (status === "all" || s.status === status) && (!q || s.name.toLowerCase().includes(q.toLowerCase()) || s.id.toLowerCase().includes(q.toLowerCase()) || s.apaar.endsWith(q)));
    r = [...r].sort((a, b) => (a[sort.k] > b[sort.k] ? 1 : -1) * sort.dir);
    return r;
  }, [data, q, prog, status, sort]);
  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const view = rows.slice(page * PAGE, page * PAGE + PAGE);
  const toggle = (k: SortKey) => setSort((s) => ({ k, dir: s.k === k ? (s.dir === 1 ? -1 : 1) : 1 }));
  const H = ({ k, children }: { k: SortKey; children: string }) => (
    <th className={th}><button onClick={() => toggle(k)} className="inline-flex items-center gap-1 uppercase hover:text-foreground">{children}<ArrowUpDown className="size-3" /></button></th>
  );

  return (
    <>
      <PageHeader crumbs={[{ label: "Student Records" }, { label: "Students" }]} title="Students" description="Student identity records. APAAR identifiers are masked by default." actions={<Button asChild><Link to="/students/new"><Plus className="size-4" /> Register student</Link></Button>} />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative min-w-64 flex-1 sm:max-w-sm">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={q} onChange={(e) => { setQ(e.target.value); setPage(0); }} placeholder="Search name, record ID or last 4 digits" className="bg-surface pl-9" aria-label="Search students" />
        </div>
        <Select value={prog} onValueChange={(v) => { setProg(v); setPage(0); }}>
          <SelectTrigger className="w-52 bg-surface" aria-label="Programme filter"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value="all">All programmes</SelectItem>{programmes.map((p) => <SelectItem key={p.code} value={p.code}>{p.code}</SelectItem>)}</SelectContent>
        </Select>
        <Select value={status} onValueChange={(v) => { setStatus(v); setPage(0); }}>
          <SelectTrigger className="w-48 bg-surface" aria-label="Status filter"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value="all">All statuses</SelectItem>{["Verified", "Pending review", "Flagged", "Correction requested", "Draft"].map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
        </Select>
        <span className="ml-auto text-xs text-muted-foreground">{rows.length} records</span>
      </div>

      <div className="overflow-x-auto rounded-md border bg-surface shadow-subtle">
        <table className="w-full min-w-[900px]">
          <thead className="bg-muted/50"><tr><H k="name">Student</H><th className={th}>APAAR ID</th><H k="programme">Programme</H><H k="admissionYear">Year</H><th className={th}>Category</th><th className={th}>Status</th><H k="updated">Last updated</H><th className={th}><span className="sr-only">Actions</span></th></tr></thead>
          <tbody>
            {isLoading && Array.from({ length: 8 }).map((_, i) => <tr key={i} className="border-t">{Array.from({ length: 8 }).map((_, j) => <td key={j} className={td}><Skeleton className="h-4 w-full" /></td>)}</tr>)}
            {!isLoading && view.map((s: Student) => (
              <tr key={s.id} className={tr}>
                <td className={td}><Link to="/students/$id" params={{ id: s.id }} className="font-medium hover:text-primary">{s.name}</Link><div className="text-xs text-muted-foreground">{s.id}</div></td>
                <td className={`${td} font-mono text-xs`}>{maskApaar(s.apaar)}</td>
                <td className={td}>{s.programme}</td>
                <td className={`${td} tabular-nums`}>{s.admissionYear}</td>
                <td className={td}>{s.category}</td>
                <td className={td}><StatusBadge value={s.status} /></td>
                <td className={`${td} text-muted-foreground`}>{fmtDate(s.updated)}</td>
                <td className={`${td} text-right`}><Button variant="ghost" size="sm" asChild><Link to="/students/$id" params={{ id: s.id }}>View</Link></Button></td>
              </tr>
            ))}
          </tbody>
        </table>
        {isError && <div className="flex items-center justify-center gap-3 border-t p-8 text-sm text-destructive"><AlertTriangle className="size-4" /> Records could not be loaded. <Button size="sm" variant="outline" onClick={() => refetch()}>Retry</Button></div>}
        {!isLoading && !isError && rows.length === 0 && <EmptyState title="No matching records" body="Try a different search term or clear the filters." action={<Button variant="outline" size="sm" onClick={() => { setQ(""); setProg("all"); setStatus("all"); }}>Clear filters</Button>} />}
        {rows.length > 0 && (
          <div className="flex items-center justify-between border-t px-4 py-3 text-xs text-muted-foreground">
            <span>Showing {page * PAGE + 1}–{Math.min(rows.length, (page + 1) * PAGE)} of {rows.length}</span>
            <div className="flex items-center gap-1">
              <Button variant="outline" size="icon" className="size-8" disabled={page === 0} onClick={() => setPage(page - 1)} aria-label="Previous page"><ChevronLeft className="size-4" /></Button>
              <span className="px-2">Page {page + 1} of {pages}</span>
              <Button variant="outline" size="icon" className="size-8" disabled={page >= pages - 1} onClick={() => setPage(page + 1)} aria-label="Next page"><ChevronRight className="size-4" /></Button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
