import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Link } from "@tanstack/react-router";
import { ChevronRight, Inbox } from "lucide-react";

export function Wordmark({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <img src="/favicon-32x32.png" alt="APAAR Platform Logo" className="size-8 shrink-0 rounded-lg object-contain shadow-sm" />
      {!compact && (
        <div className="leading-tight">
          <div className="font-display text-[15px] font-bold tracking-[0.14em]">APAAR</div>
          <div className="text-[10.5px] text-navy-muted">Academic Identity &amp; Student Records</div>
        </div>
      )}
    </div>
  );
}

export function PageHeader({ crumbs, title, description, actions }: { crumbs: { label: string; to?: string }[]; title: string; description?: string; actions?: ReactNode }) {
  return (
    <header className="mb-8 border-b pb-6">
      <nav aria-label="Breadcrumb" className="mb-3 flex items-center gap-1 text-xs text-muted-foreground">
        {crumbs.map((c, i) => (
          <span key={i} className="flex items-center gap-1">
            {i > 0 && <ChevronRight className="size-3" />}
            {c.to ? <Link to={c.to} className="hover:text-foreground">{c.label}</Link> : <span className="text-foreground">{c.label}</span>}
          </span>
        ))}
      </nav>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{title}</h1>
          {description && <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{description}</p>}
        </div>
        {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
      </div>
    </header>
  );
}

const tones = {
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  error: "bg-error-soft text-destructive",
  info: "bg-info-soft text-primary",
  teal: "bg-teal-soft text-teal",
  neutral: "bg-muted text-muted-foreground",
} as const;
export type Tone = keyof typeof tones;

const statusTone: Record<string, Tone> = {
  Verified: "success", Completed: "success", Resolved: "success", Success: "success", Active: "success", Submitted: "success",
  "Pending review": "warning", "Under review": "warning", "Completed with errors": "warning", Medium: "warning", "In progress": "warning", Processing: "info",
  Flagged: "error", Failed: "error", Escalated: "error", High: "error", Denied: "error", Suspended: "error",
  Open: "info", "Correction requested": "teal", Low: "neutral", Draft: "neutral", "Not started": "neutral",
};

export function StatusBadge({ value, tone }: { value: string; tone?: Tone }) {
  const t = tone ?? statusTone[value] ?? "neutral";
  return (
    <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap rounded-sm px-2 py-0.5 text-xs font-medium", tones[t])}>
      <span className="size-1.5 rounded-full bg-current" aria-hidden />
      {value}
    </span>
  );
}

export function Section({ title, description, actions, children, className }: { title: string; description?: string; actions?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-md border bg-surface shadow-subtle", className)}>
      <div className="flex items-start justify-between gap-4 border-b px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold">{title}</h2>
          {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
        </div>
        {actions}
      </div>
      {children}
    </section>
  );
}

export function EmptyState({ title, body, action }: { title: string; body: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center px-6 py-14 text-center">
      <div className="mb-3 grid size-10 place-items-center rounded-full bg-muted"><Inbox className="size-5 text-muted-foreground" /></div>
      <p className="text-sm font-medium">{title}</p>
      <p className="mt-1 max-w-sm text-xs text-muted-foreground">{body}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function SimulatedBanner() {
  return (
    <div role="status" className="demo-stripes rounded-md border border-warning/40 px-4 py-2.5 text-center text-xs font-bold tracking-[0.12em] text-warning">
      SIMULATED — NOT OFFICIAL APAAR VERIFICATION
    </div>
  );
}

export const th = "h-10 px-4 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground";
export const td = "px-4 py-3 text-sm";
export const tr = "border-t transition-colors hover:bg-accent/40";

export function fmtDate(iso: string, withTime = false) {
  const d = new Date(iso);
  return d.toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}) });
}
