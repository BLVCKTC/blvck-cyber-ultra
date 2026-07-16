"use client"

import { useState } from "react"
import {
  LayoutDashboard,
  Radar,
  Bug,
  HeartPulse,
  Globe2,
  FileBarChart,
  Bot,
  ShieldHalf,
  Settings,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"

const nav = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "threat-center", label: "Threat Center", icon: Radar },
  { id: "security-testing", label: "Security Testing", icon: Bug },
  { id: "health", label: "Health Monitor", icon: HeartPulse },
  { id: "threat-intel", label: "Threat Intel", icon: Globe2 },
  { id: "reports", label: "Reports", icon: FileBarChart },
  { id: "assistant", label: "AI Assistant", icon: Bot },
]

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [active, setActive] = useState("overview")

  const handleClick = (id: string) => {
    setActive(id)
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" })
    onClose()
  }

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-background/70 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-sidebar-border bg-sidebar transition-transform lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between gap-2 border-b border-sidebar-border px-5 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary glow-primary">
              <ShieldHalf className="h-5 w-5" />
            </div>
            <div className="leading-tight">
              <p className="font-mono text-sm font-bold tracking-wider text-foreground">
                BLVCK<span className="text-primary">CYBER</span>
              </p>
              <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">AI-SOC</p>
            </div>
          </div>
          <button
            className="rounded p-1 text-muted-foreground hover:text-foreground lg:hidden"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {nav.map((item) => {
            const Icon = item.icon
            const isActive = active === item.id
            return (
              <button
                key={item.id}
                onClick={() => handleClick(item.id)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-foreground",
                )}
              >
                <Icon className={cn("h-4 w-4", isActive && "text-primary")} />
                <span className="font-medium">{item.label}</span>
                {isActive && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />}
              </button>
            )
          })}
        </nav>

        <div className="border-t border-sidebar-border p-3">
          <button className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent/50 hover:text-foreground">
            <Settings className="h-4 w-4" />
            <span className="font-medium">Settings</span>
          </button>
          <div className="mt-3 flex items-center gap-3 rounded-md bg-sidebar-accent/40 px-3 py-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 font-mono text-xs font-bold text-primary">
              AZ
            </div>
            <div className="min-w-0 leading-tight">
              <p className="truncate text-xs font-medium text-foreground">Amara Zulu</p>
              <p className="truncate font-mono text-[10px] text-muted-foreground">SOC Analyst · Tier 3</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
