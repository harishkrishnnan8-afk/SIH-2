import { createFileRoute, redirect } from "@tanstack/react-router";
import { pageHead } from "@/lib/head";

export const Route = createFileRoute("/")({
  head: pageHead("Welcome", "APAAR ID-based student data management and verification platform for AICTE-approved institutions."),
  beforeLoad: () => {
    throw redirect({ to: "/login" });
  },
});
