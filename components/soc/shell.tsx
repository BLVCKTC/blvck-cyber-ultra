"use client"

import { useState } from "react"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenu={() => setMenuOpen(true)} />
        <main className="cyber-grid flex-1 space-y-6 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  )
}

export function SectionHeading({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="h-8 w-1 rounded-full bg-primary" />
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-foreground text-balance">{title}</h1>
        <p className="text-xs text-muted-foreground">{sub}</p>
      </div>
    </div>
  )
}
