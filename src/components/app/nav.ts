import { LayoutDashboard, Users, ClipboardList, FileUp, ShieldAlert, Building2, BookOpen, SlidersHorizontal, BadgeCheck, FileBarChart, History, Settings, Globe2, type LucideIcon } from "lucide-react";

export type Role = "institution_admin" | "data_officer" | "central_reviewer";
export interface NavItem { title: string; to: string; icon: LucideIcon; roles?: Role[] }
export interface NavGroup { label: string; items: NavItem[] }

export const navGroups: NavGroup[] = [
  { label: "Overview", items: [
    { title: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
    { title: "Central Review", to: "/central", icon: Globe2, roles: ["central_reviewer", "institution_admin"] },
  ] },
  { label: "Student Records", items: [
    { title: "Students", to: "/students", icon: Users },
    { title: "Admissions", to: "/admissions", icon: ClipboardList },
    { title: "CSV Imports", to: "/uploads", icon: FileUp },
    { title: "Validation Findings", to: "/findings", icon: ShieldAlert },
  ] },
  { label: "Institutions", items: [
    { title: "Institutions", to: "/institutions", icon: Building2 },
    { title: "Programmes", to: "/programmes", icon: BookOpen },
    { title: "Intake Configuration", to: "/intake-configuration", icon: SlidersHorizontal, roles: ["institution_admin"] },
  ] },
  { label: "Verification & Reporting", items: [
    { title: "Verification", to: "/verification", icon: BadgeCheck },
    { title: "Reports & Exports", to: "/reports", icon: FileBarChart },
  ] },
  { label: "Governance", items: [
    { title: "Audit Trail", to: "/audit", icon: History, roles: ["institution_admin", "central_reviewer"] },
    { title: "Access & Settings", to: "/settings", icon: Settings },
  ] },
];

export const visibleGroups = (role: Role) =>
  navGroups.map((g) => ({ ...g, items: g.items.filter((i) => !i.roles || i.roles.includes(role)) })).filter((g) => g.items.length);
