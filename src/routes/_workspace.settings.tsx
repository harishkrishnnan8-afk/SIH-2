import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader, Section, th, td, tr } from "@/components/app/primitives";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/settings")({
  head: pageHead("Access & settings", "Profile, role, institution scope, security, import configuration and permissions."),
  component: Settings,
});

const pending = () => toast.info("Backend integration pending", { description: "This setting will save once the backend is connected." });
const PERMS = ["View student records", "Edit student records", "Import CSV", "Resolve findings", "Configure intake", "View audit trail", "Manage roles"];
const ROLES = { "Institution admin": [1, 1, 1, 1, 1, 1, 1], "Data officer": [1, 1, 1, 0, 0, 0, 0], "Central reviewer": [1, 0, 0, 1, 0, 1, 0] };

function Row({ label, desc, children }: { label: string; desc?: string; children: React.ReactNode }) {
  return <div className="grid gap-3 p-5 sm:grid-cols-[1fr_280px] sm:items-center"><div><div className="text-sm font-medium">{label}</div>{desc && <p className="text-xs text-muted-foreground">{desc}</p>}</div><div>{children}</div></div>;
}

function Settings() {
  return (
    <>
      <PageHeader crumbs={[{ label: "Governance" }, { label: "Access & Settings" }]} title="Access & settings" description="Controls marked as pending will work once the backend is connected." />
      <Tabs defaultValue="profile">
        <TabsList className="mb-6"><TabsTrigger value="profile">Profile</TabsTrigger><TabsTrigger value="security">Security</TabsTrigger><TabsTrigger value="imports">Import</TabsTrigger><TabsTrigger value="roles">Roles & permissions</TabsTrigger></TabsList>
        <TabsContent value="profile" className="space-y-6">
          <Section title="Profile"><div className="divide-y">
            <Row label="Full name"><Input defaultValue="Priya Nair" aria-label="Full name" /></Row>
            <Row label="Email"><Input defaultValue="priya.nair@example.edu" aria-label="Email" /></Row>
          </div></Section>
          <Section title="Role & scope"><div className="divide-y">
            <Row label="Role" desc="Assigned by a central administrator."><span className="text-sm">Institution admin</span></Row>
            <Row label="Institution scope"><span className="text-sm">Demo Institute of Technology, North Campus</span></Row>
          </div></Section>
          <div className="flex justify-end"><Button onClick={pending}>Save profile</Button></div>
        </TabsContent>
        <TabsContent value="security">
          <Section title="Security"><div className="divide-y">
            <Row label="Two-factor authentication" desc="Pending backend integration."><Switch onCheckedChange={pending} aria-label="Two-factor authentication" /></Row>
            <Row label="Session timeout" desc="Sign out after inactivity."><Input type="number" defaultValue={15} aria-label="Session timeout minutes" /></Row>
            <Row label="Password"><Button variant="outline" onClick={pending}>Change password</Button></Row>
          </div></Section>
        </TabsContent>
        <TabsContent value="imports">
          <Section title="Import configuration"><div className="divide-y">
            <Row label="Reject file on any error" desc="Otherwise valid rows are accepted and errors reported."><Switch onCheckedChange={pending} aria-label="Reject file on error" /></Row>
            <Row label="Warn on duplicate filenames"><Switch defaultChecked onCheckedChange={pending} aria-label="Warn on duplicates" /></Row>
            <Row label="Maximum rows per file"><Input type="number" defaultValue={5000} aria-label="Maximum rows" /></Row>
          </div></Section>
        </TabsContent>
        <TabsContent value="roles">
          <Section title="Role permissions" description="Read-only preview. Managed by the backend.">
            <div className="overflow-x-auto"><table className="w-full min-w-[600px]">
              <thead><tr><th className={th}>Permission</th>{Object.keys(ROLES).map((r) => <th key={r} className={`${th} text-center`}>{r}</th>)}</tr></thead>
              <tbody>{PERMS.map((p, i) => <tr key={p} className={tr}><td className={td}>{p}</td>{Object.values(ROLES).map((v, j) => <td key={j} className={`${td} text-center`}>{v[i] ? <span className="text-success">●</span> : <span className="text-muted-foreground">—</span>}</td>)}</tr>)}</tbody>
            </table></div>
          </Section>
        </TabsContent>
      </Tabs>
    </>
  );
}
