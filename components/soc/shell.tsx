'use client'

import { useState } from 'react'

import { Sidebar } from '@/components/shell/sidebar'
import { Topbar } from '@/components/soc/topbar'

export type AuthUser = {
  id: number
  name?: string | null
  email?: string | null
  role?: string | null
  tenantId?: string | null
}

export type DashboardShellProps = {
  children: React.ReactNode

  user?: AuthUser | null

  permissions?: string[]

  tenantId?: string
}

export function DashboardShell({
  children,
  user,
  permissions = [],
  tenantId,
}: DashboardShellProps) {
  const [menuOpen, setMenuOpen] = useState(false)

  if (!tenantId) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        tenantId={tenantId}
        permissions={permissions}
        user={{
          name: user?.name ?? 'User',

          email: user?.email ?? '',

          role: user?.role ?? 'Member',
        }}
      />

      <div
        className="
          flex
          min-h-screen
          flex-col

          lg:pl-64
        "
      >
        <Topbar onMenu={() => setMenuOpen(true)} user={user} />

        <main
          className="
            cyber-grid
            flex-1
            space-y-6
            p-4
            lg:p-6
          "
        >
          {children}
        </main>
      </div>
    </div>
  )
}

export function SectionHeading({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="h-8 w-1 rounded-full bg-primary" />

      <div>
        <h1
          className="
          text-lg
          font-semibold
          tracking-tight
          text-foreground
          text-balance
        "
        >
          {title}
        </h1>

        <p className="text-xs text-muted-foreground">{sub}</p>
      </div>
    </div>
  )
}
