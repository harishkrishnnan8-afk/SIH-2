import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader } from "@/components/app/primitives";
import { programmes } from "@/lib/demo/data";
import { saveStudent } from "@/lib/services";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/_workspace/students/new")({
  head: pageHead("Register student", "Register a student identity and admission record with an APAAR identifier."),
  component: NewStudent,
});

export const studentSchema = z.object({
  name: z.string().trim().min(2, "Enter the student's full name.").max(120),
  apaar: z.string().regex(/^\d{12}$/, "APAAR identifier must be exactly 12 digits."),
  programme: z.string().min(1, "Select a programme."),
  year: z.string().min(1, "Select an academic year."),
  category: z.string().min(1, "Select an admission category."),
  status: z.string().min(1, "Select an admission status."),
  nri: z.boolean(),
  oci: z.boolean(),
  ociCard: z.string().optional(),
  foreign: z.boolean(),
  nationality: z.string().optional(),
});
type F = z.infer<typeof studentSchema>;

function Req() { return <span className="text-destructive" aria-hidden> *</span>; }
function Err({ id, msg }: { id: string; msg?: string | undefined }) { return msg ? <p id={id} role="alert" className="text-xs text-destructive">{msg}</p> : null; }

function NewStudent() {
  const nav = useNavigate();
  const { register, control, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<F>({
    resolver: zodResolver(studentSchema),
    defaultValues: { name: "", apaar: "", programme: "", year: "2026–27", category: "", status: "", nri: false, oci: false, foreign: false },
  });
  const oci = watch("oci"); const foreign = watch("foreign");

  const onSubmit = async (values: F) => {
    try {
      const res = await saveStudent(values);
      if (res.persisted) {
        toast.success("Student record saved", { description: "Record successfully persisted to the database." });
        nav({ to: "/students" });
      } else {
        toast.warning("Not saved — backend not connected", { description: "The form is valid, but this demo cannot persist records." });
      }
    } catch (err: unknown) {
      toast.error("Failed to save student", { description: err instanceof Error ? err.message : "An unexpected error occurred." });
    }
  };

  const sel = (name: "programme" | "year" | "category" | "status", label: string, opts: string[]) => (
    <div className="space-y-1.5">
      <Label htmlFor={name}>{label}<Req /></Label>
      <Controller control={control} name={name} render={({ field }) => (
        <Select value={field.value} onValueChange={field.onChange}>
          <SelectTrigger id={name} aria-invalid={!!errors[name]} aria-describedby={`${name}-err`}><SelectValue placeholder="Select…" /></SelectTrigger>
          <SelectContent>{opts.map((o) => <SelectItem key={o} value={o}>{o}</SelectItem>)}</SelectContent>
        </Select>
      )} />
      <Err id={`${name}-err`} msg={errors[name]?.message} />
    </div>
  );

  return (
    <>
      <PageHeader crumbs={[{ label: "Students", to: "/students" }, { label: "Register" }]} title="Register student" description="Fields marked * are required. Identity and admission details are stored as separate records." />
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="max-w-4xl space-y-10">
        <fieldset className="grid gap-x-8 gap-y-5 md:grid-cols-[220px_1fr]">
          <legend className="contents"><div><h2 className="text-sm font-semibold">Student identity</h2><p className="mt-1 text-xs text-muted-foreground">Who the student is, independent of any admission.</p></div></legend>
          <div className="grid gap-5 rounded-md border bg-surface p-6 sm:grid-cols-2">
            <div className="space-y-1.5 sm:col-span-2"><Label htmlFor="name">Student name<Req /></Label><Input id="name" {...register("name")} aria-invalid={!!errors.name} aria-describedby="name-err" /><Err id="name-err" msg={errors.name?.message} /></div>
            <div className="space-y-1.5 sm:col-span-2"><Label htmlFor="apaar">APAAR identifier<Req /></Label><Input id="apaar" inputMode="numeric" maxLength={12} className="font-mono" {...register("apaar")} aria-invalid={!!errors.apaar} aria-describedby="apaar-err apaar-hint" /><p id="apaar-hint" className="text-xs text-muted-foreground">12 digits. Will be masked after saving.</p><Err id="apaar-err" msg={errors.apaar?.message} /></div>
          </div>
        </fieldset>

        <fieldset className="grid gap-x-8 gap-y-5 md:grid-cols-[220px_1fr]">
          <legend className="contents"><div><h2 className="text-sm font-semibold">Admission</h2><p className="mt-1 text-xs text-muted-foreground">The admission record for this academic year.</p></div></legend>
          <div className="grid gap-5 rounded-md border bg-surface p-6 sm:grid-cols-2">
            {sel("programme", "Programme", programmes.map((p) => p.code))}
            {sel("year", "Academic year", ["2026–27", "2025–26", "2024–25"])}
            {sel("category", "Admission category", ["General", "Supernumerary", "NRI", "OCI", "Foreign National"])}
            {sel("status", "Admission status", ["Admitted", "Provisional", "Withdrawn"])}
          </div>
        </fieldset>

        <fieldset className="grid gap-x-8 gap-y-5 md:grid-cols-[220px_1fr]">
          <legend className="contents"><div><h2 className="text-sm font-semibold">Residency & nationality</h2><p className="mt-1 text-xs text-muted-foreground">Additional details appear when applicable.</p></div></legend>
          <div className="divide-y rounded-md border bg-surface">
            {([["nri", "NRI category", "Student is admitted under the NRI category."], ["oci", "OCI status", "Student holds Overseas Citizenship of India."], ["foreign", "Foreign national", "Student is a foreign national."]] as const).map(([k, l, d]) => (
              <div key={k} className="flex items-center justify-between gap-4 p-5">
                <div><Label htmlFor={k}>{l}</Label><p className="text-xs text-muted-foreground">{d}</p></div>
                <Controller control={control} name={k} render={({ field }) => <Switch id={k} checked={field.value} onCheckedChange={field.onChange} />} />
              </div>
            ))}
            {oci && <div className="space-y-1.5 bg-muted/40 p-5 animate-in fade-in"><Label htmlFor="ociCard">OCI card reference</Label><Input id="ociCard" {...register("ociCard")} /></div>}
            {foreign && <div className="space-y-1.5 bg-muted/40 p-5 animate-in fade-in"><Label htmlFor="nationality">Nationality</Label><Input id="nationality" {...register("nationality")} /></div>}
          </div>
        </fieldset>

        <div className="flex justify-end gap-3 border-t pt-6">
          <Button type="button" variant="outline" onClick={() => nav({ to: "/students" })}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>{isSubmitting && <Loader2 className="size-4 animate-spin" />}Save record</Button>
        </div>
      </form>
    </>
  );
}
