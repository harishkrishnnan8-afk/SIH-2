import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Eye, EyeOff, Loader2, ShieldCheck, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Wordmark } from "@/components/app/primitives";
import { pageHead } from "@/lib/head";
import { loginUser } from "@/lib/services";
import { toast } from "sonner";

export const Route = createFileRoute("/login")({
  head: pageHead("Sign in", "Sign in to the APAAR Student Data Platform for institutional administrators and reviewers."),
  component: Login,
});

function Login() {
  const nav = useNavigate();
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ user?: string; pass?: string; form?: string }>({});

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const user = String(fd.get("user") ?? "").trim();
    const pass = String(fd.get("pass") ?? "");
    const next: typeof errors = {};
    if (!user) next.user = "Enter your username or institutional email.";
    if (pass.length < 8) next.pass = "Password must be at least 8 characters.";
    setErrors(next);
    if (Object.keys(next).length) return;
    setLoading(true);
    try {
      await loginUser(user, pass);
      toast.success("Signed in successfully");
      nav({ to: "/dashboard" });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed.";
      setErrors({ form: msg });
      toast.error("Sign-in failed", { description: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <aside className="relative hidden overflow-hidden bg-navy p-12 text-navy-foreground lg:flex lg:flex-col">
        <Wordmark />
        <svg className="absolute -right-24 top-1/2 size-[560px] -translate-y-1/2 opacity-40" viewBox="0 0 400 400" aria-hidden>
          {Array.from({ length: 9 }).map((_, i) => (
            <circle key={i} cx="200" cy="200" r={30 + i * 20} fill="none" className="stroke-navy-muted" strokeWidth="0.6" strokeDasharray={i % 2 ? "2 6" : undefined} />
          ))}
          <circle cx="170" cy="200" r="48" fill="none" className="stroke-primary" strokeWidth="2" />
          <circle cx="230" cy="200" r="48" fill="none" className="stroke-teal" strokeWidth="2" />
        </svg>
        <div className="relative mt-auto max-w-md">
          <div className="eyebrow mb-4 text-navy-muted">SIH26263 · AICTE Regulation Bureau</div>
          <h1 className="text-4xl font-semibold leading-tight">One academic identity.<br />Records you can stand behind.</h1>
          <p className="mt-4 text-sm leading-relaxed text-navy-muted">
            Manage admissions, validate student data against APAAR identifiers, and prepare intake reports for review.
          </p>
        </div>
      </aside>

      <main className="flex flex-col justify-center px-6 py-12 sm:px-16">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-10 rounded-md bg-navy p-3 text-navy-foreground lg:hidden"><Wordmark /></div>
          <h2 className="text-2xl font-semibold">Sign in</h2>
          <p className="mt-1.5 text-sm text-muted-foreground">Use your institutional account credentials.</p>

          <form onSubmit={submit} noValidate className="mt-8 space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="user">Username or email <span className="text-destructive">*</span></Label>
              <Input id="user" name="user" autoComplete="username" aria-invalid={!!errors.user} aria-describedby={errors.user ? "user-err" : undefined} />
              {errors.user && <p id="user-err" className="flex items-center gap-1 text-xs text-destructive"><AlertCircle className="size-3" />{errors.user}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="pass">Password <span className="text-destructive">*</span></Label>
              <div className="relative">
                <Input id="pass" name="pass" type={show ? "text" : "password"} autoComplete="current-password" className="pr-10" aria-invalid={!!errors.pass} aria-describedby={errors.pass ? "pass-err" : undefined} />
                <button type="button" onClick={() => setShow((s) => !s)} className="absolute inset-y-0 right-0 grid w-10 place-items-center text-muted-foreground hover:text-foreground" aria-label={show ? "Hide password" : "Show password"}>
                  {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              </div>
              {errors.pass && <p id="pass-err" className="flex items-center gap-1 text-xs text-destructive"><AlertCircle className="size-3" />{errors.pass}</p>}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="size-4 animate-spin" />} {loading ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          <div className="mt-8 rounded-md border border-warning/40 bg-warning-soft p-4 text-xs leading-relaxed text-warning">
            <div className="mb-1 flex items-center gap-1.5 font-semibold"><ShieldCheck className="size-4" /> Demo sign-in only</div>
            This screen does not perform secure authentication. Any valid-looking input opens the demo workspace with synthetic data. Production sign-in must be handled by the backend.
          </div>
        </div>
      </main>
    </div>
  );
}
