"use client"

import { useEffect, useState } from "react"
import { Menu, Bell, Search, Building2 } from "lucide-react"

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const [clock, setClock] = useState("")

  useEffect(() => {
    const tick = () =>
      setClock(
        new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) + " UTC",
      )
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-border bg-background/80 px-4 py-3 backdrop-blur-md lg:px-6">
      <button
        className="rounded p-1.5 text-muted-foreground hover:text-foreground lg:hidden"
        onClick={onMenu}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="hidden items-center gap-2 rounded-md border border-border bg-card/60 px-3 py-1.5 sm:flex">
        <Building2 className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium text-foreground">Zenith Bank Group</span>
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">· Enterprise</span>
      </div>

      <div className="relative ml-auto hidden max-w-xs flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search threats, assets, CVEs…"
          className="w-full rounded-md border border-border bg-card/60 py-2 pl-9 pr-3 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none"
        />
      </div>

      <div className="ml-auto flex items-center gap-3 md:ml-0">
        <div className="hidden items-center gap-2 rounded-md border border-success/30 bg-success/10 px-3 py-1.5 sm:flex">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
          </span>
          <span className="font-mono text-[11px] font-medium uppercase tracking-wider text-success">
            Monitoring Live
          </span>
        </div>

        <span className="hidden font-mono text-xs text-muted-foreground lg:inline">{clock}</span>

        <button
          className="relative rounded-md border border-border bg-card/60 p-2 text-muted-foreground hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-critical font-mono text-[9px] font-bold text-background">
            5
          </span>
        </button>
      </div>
    </header>
  )
}
