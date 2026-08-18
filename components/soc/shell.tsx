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

        <main className="mx-auto w-full max-w-[1600px] flex-1 space-y-6 px-4 py-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  )
}

export function SectionHeading({
  title,
  sub,
  action,
}: {
  title: string
  sub: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        <h1 className="text-balance text-xl font-semibold tracking-tight text-foreground">
          {title}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{sub}</p>
      </div>
      {action}
    </div>
  )
}
