import type { Metadata } from "next"
import { DashboardShell } from "@/components/soc/shell"

export const metadata: Metadata = {
  title: "AI-SOC Dashboard — BLVCK CYBER",
  description: "Real-time security operations center dashboard.",
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>
}
