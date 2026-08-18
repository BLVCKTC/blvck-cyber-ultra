'use client'

import { Menu } from 'lucide-react'

import { cn } from '@/lib/utils'
import { buildNavSections } from '@/lib/nav'

import { SidebarHeader } from './sidebar-header'
import { SidebarSection } from './sidebar-section'
import { SidebarUser } from './sidebar-user'

export type SidebarProps = {
  open?: boolean

  onClose?: () => void

  tenantId: string

  permissions?: string[]

  user?: {
    name?: string
    email?: string
    role?: string
    avatarUrl?: string
  }
}

export function Sidebar({
  open = false,
  onClose,
  tenantId,
  permissions = [],
  user,
}: SidebarProps) {
  const navSections = buildNavSections(tenantId, permissions)

  return (
    <>
      {/* Mobile overlay */}

      {open && (
        <div
          className="
            fixed
            inset-0
            z-40
            bg-black/50
            lg:hidden
          "
          onClick={onClose}
        />
      )}

      {/* Sidebar */}

      <aside
        className={cn(
          `
          fixed
          inset-y-0
          left-0
          z-50

          flex
          w-64
          flex-col

          border-r
          border-sidebar-border

          bg-sidebar

          transition-transform
          duration-300

          lg:translate-x-0

          overflow-hidden
          `,

          open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        )}
      >
        <SidebarHeader mobile onClose={onClose} />

        <nav
          className="
            flex-1
            overflow-y-auto

            space-y-4

            px-3
            py-4

            [scrollbar-color:var(--color-sidebar-border)_transparent]
            [scrollbar-width:thin]
          "
        >
          {navSections.map((section) => (
            <SidebarSection
              key={section.label}
              title={section.label}
              items={section.items}
              tenantId={tenantId}
              onNavigate={onClose}
            />
          ))}
        </nav>

        <SidebarUser
          name={user?.name}
          email={user?.email}
          role={user?.role}
          avatarUrl={user?.avatarUrl}
        />
      </aside>
    </>
  )
}
