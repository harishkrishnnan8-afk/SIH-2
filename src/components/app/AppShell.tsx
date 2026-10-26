import { useState, type ReactNode } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { Bell, Menu, PanelLeftClose, PanelLeftOpen, LogOut, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Wordmark } from "./primitives";
import { visibleGroups, type Role } from "./nav";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { findings } from "@/lib/demo/data";
import { logoutUser } from "@/lib/services";

const ROLE: Role = "institution_admin";

function SidebarNav({ collapsed, onNavigate }: { collapsed: boolean; onNavigate?: () => void }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  return (
    <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Primary">
      {visibleGroups(ROLE).map((g) => (
        <div key={g.label} className="mb-5">
          {!collapsed && <div className="eyebrow mb-1.5 px-2.5 text-navy-muted/70">{g.label}</div>}
          <ul className="space-y-0.5">
            {g.items.map((it) => {
              const active = path === it.to || path.startsWith(it.to + "/");
              return (
                <li key={it.to}>
                  <Link
                    to={it.to}
                    onClick={onNavigate}
                    title={collapsed ? it.title : undefined}
                    className={cn(
                      "relative flex items-center gap-3 rounded-sm px-2.5 py-2 text-[13px] text-navy-muted transition-colors hover:bg-navy-hover hover:text-navy-foreground",
                      active && "bg-navy-hover font-medium text-navy-foreground before:absolute before:inset-y-1.5 before:left-0 before:w-0.5 before:rounded-full before:bg-primary",
                      collapsed && "justify-center",
                    )}
                  >
                    <it.icon className="size-4 shrink-0" />
                    {!collapsed && <span className="truncate">{it.title}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobile, setMobile] = useState(false);
  const path = useRouterState({ select: (s) => s.location.pathname });
  const open = findings.filter((f) => f.status === "Open").length;

  return (
    <div className="flex min-h-screen w-full">
      <aside className={cn("sticky top-0 hidden h-screen shrink-0 flex-col bg-navy text-navy-foreground transition-[width] duration-200 lg:flex", collapsed ? "w-[68px]" : "w-64")}>
        <div className={cn("flex h-16 items-center border-b border-navy-line px-4", collapsed && "justify-center px-0")}>
          <Wordmark compact={collapsed} />
        </div>
        <SidebarNav collapsed={collapsed} />
        <button onClick={() => setCollapsed((c) => !c)} className="flex items-center gap-2 border-t border-navy-line px-5 py-3 text-xs text-navy-muted hover:text-navy-foreground" aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
          {collapsed ? <PanelLeftOpen className="size-4" /> : <><PanelLeftClose className="size-4" /> Collapse</>}
        </button>
      </aside>

      {mobile && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-navy/50 animate-in fade-in" onClick={() => setMobile(false)} />
          <aside className="absolute inset-y-0 left-0 flex w-72 flex-col bg-navy text-navy-foreground animate-in slide-in-from-left">
            <div className="flex h-16 items-center justify-between border-b border-navy-line px-4">
              <Wordmark />
              <button onClick={() => setMobile(false)} aria-label="Close menu"><X className="size-5" /></button>
            </div>
            <SidebarNav collapsed={false} onNavigate={() => setMobile(false)} />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="demo-stripes border-b border-warning/30 py-1 text-center text-[11px] font-bold tracking-[0.14em] text-warning">
          DEMO ENVIRONMENT — SYNTHETIC DATA
        </div>
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b bg-surface/95 px-4 backdrop-blur md:px-8">
          <button className="lg:hidden" onClick={() => setMobile(true)} aria-label="Open menu"><Menu className="size-5" /></button>
          <div className="hidden text-xs text-muted-foreground sm:block">
            <span className="font-medium text-foreground">Demo Institute of Technology</span> · Academic year 2026–27
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Link to="/findings" className="relative grid size-9 place-items-center rounded-sm hover:bg-muted" aria-label={`${open} open findings`}>
              <Bell className="size-4" />
              {open > 0 && <span className="absolute right-1.5 top-1.5 grid min-w-4 place-items-center rounded-full bg-destructive px-1 text-[10px] font-semibold text-destructive-foreground">{open}</span>}
            </Link>
            <DropdownMenu>
              <DropdownMenuTrigger className="flex items-center gap-2.5 rounded-sm px-2 py-1 hover:bg-muted">
                <span className="grid size-8 place-items-center rounded-full bg-navy text-xs font-semibold text-navy-foreground">PN</span>
                <span className="hidden text-left leading-tight md:block">
                  <span className="block text-xs font-medium">Priya Nair</span>
                  <span className="block text-[11px] text-muted-foreground">Institution admin</span>
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">Signed in as demo user</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild><Link to="/settings">Access &amp; settings</Link></DropdownMenuItem>
                <DropdownMenuItem asChild><Link to="/login" onClick={() => logoutUser()}><LogOut className="size-4" /> Sign out</Link></DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <main key={path} className="page-enter mx-auto w-full max-w-[1400px] flex-1 px-4 py-8 md:px-8">{children}</main>
      </div>
    </div>
  );
}
