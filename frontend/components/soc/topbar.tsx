'use client'

import { useEffect, useState } from 'react'
import { Menu, Bell, Search, Building2 } from 'lucide-react'
import { useTenant } from '@/components/providers/tenant-provider'
import type { AuthUser } from './shell'

export function Topbar({
  onMenu,
  user,
}: {
  onMenu: () => void
  user?: AuthUser | null
}) {
  const [clock, setClock] = useState('')
  const { organizationName, tier, role } = useTenant()

  useEffect(() => {
    const tick = () =>
      setClock(
        new Date().toLocaleTimeString('en-GB', {
          hour: '2-digit',
          minute: '2-digit',
        }) + ' UTC',
      )
    tick()
    const id = setInterval(tick, 30_000)
    return () => clearInterval(id)
  }, [])

  const displayRole = user?.role ?? role ?? 'Viewer'

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-border bg-background/85 px-4 backdrop-blur lg:px-8">
      {/* Mobile menu */}
      <button
        className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground lg:hidden"
        onClick={onMenu}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Tenant */}
      <div className="hidden items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5 sm:flex">
        <Building2 className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium text-foreground">
          {organizationName}
        </span>
        <span className="text-xs capitalize text-muted-foreground">
          · {tier}
        </span>
      </div>

      {/* Search */}
      <div className="relative ml-auto hidden max-w-sm flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="search"
          placeholder="Search alerts, assets, CVEs, IOCs…"
          className="h-9 w-full rounded-md border border-border bg-card pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-1 focus:ring-primary/40"
        />
      </div>

      <div className="ml-auto flex items-center gap-3 md:ml-0">
        {/* Live monitoring — calm, no neon ping */}
        <div className="hidden items-center gap-2 rounded-md border border-success/25 bg-success/10 px-2.5 py-1.5 sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-success" />
          <span className="text-xs font-medium text-success">Live</span>
        </div>

        {/* Clock */}
        <span className="hidden text-sm tabular text-muted-foreground lg:inline">
          {clock}
        </span>

        {/* Notifications */}
        <button
          className="relative rounded-md border border-border bg-card p-2 text-muted-foreground transition-colors hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-critical text-[9px] font-bold text-white">
            5
          </span>
        </button>

        {/* User */}
        <div className="hidden text-right lg:block">
          <p className="text-xs font-medium text-foreground">
            {user?.name ?? user?.email ?? 'Unknown User'}
          </p>
          <p className="text-[11px] capitalize text-muted-foreground">
            {displayRole}
          </p>
        </div>
      </div>
    </header>
  )
}
