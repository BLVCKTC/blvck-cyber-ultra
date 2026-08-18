'use client'

import { useMemo } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { Check, ChevronsUpDown } from 'lucide-react'

import { cn } from '@/lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  useTenant,
  type TenantMembership,
} from '@/components/providers/tenant-provider'

/**
 * Formats a raw role string ("soc_manager", "incident-responder") into the
 * existing BLVCK CYBER metadata language ("SOC MANAGER", "INCIDENT RESPONDER").
 */
function formatRole(role?: string) {
  if (!role) {
    return ''
  }

  return role.replace(/[_-]+/g, ' ').trim().toUpperCase()
}

/**
 * Replaces the `[tenantId]` segment of the current dashboard path with the
 * target tenant, preserving the functional area where safe.
 *
 * `/dashboard/tenant-a/alerts` -> `/dashboard/tenant-b/alerts`
 *
 * Falls back to `/dashboard/{tenantId}` when the path shape is unexpected.
 */
function buildTenantPath(pathname: string | null, nextTenantId: string) {
  const fallback = `/dashboard/${nextTenantId}`

  if (!pathname) {
    return fallback
  }

  const segments = pathname.split('/')

  // segments: ["", "dashboard", "{tenantId}", ...rest]
  if (segments[1] !== 'dashboard' || segments.length < 3) {
    return fallback
  }

  segments[2] = nextTenantId

  return segments.join('/') || fallback
}

export function TenantSwitcher() {
  const router = useRouter()
  const pathname = usePathname()

  const { tenantId, organizationName, role, memberships } = useTenant()

  const activeRole = useMemo(() => {
    const active = memberships.find((m) => m.tenant_id === tenantId)

    return formatRole(active?.role ?? role)
  }, [memberships, tenantId, role])

  const handleSelect = (membership: TenantMembership) => {
    if (membership.tenant_id === tenantId) {
      return
    }

    router.push(buildTenantPath(pathname, membership.tenant_id))
  }

  // Single-tenant (or unknown) users see the organization presented statically,
  // identical to the previous experience — no dropdown, no chevron.
  if (memberships.length <= 1) {
    return (
      <div className="flex min-w-0 flex-col">
        <span
          className="truncate text-sm font-semibold tracking-wide text-foreground"
          title={organizationName}
        >
          {organizationName}
        </span>

        {activeRole ? (
          <span className="truncate font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            {activeRole}
          </span>
        ) : null}
      </div>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className={cn(
          'group flex min-w-0 items-center gap-1.5 rounded-md px-1.5 py-1 text-left',
          'outline-none transition-colors',
          'hover:bg-sidebar-accent/60 focus-visible:bg-sidebar-accent/60',
          'data-[popup-open]:bg-sidebar-accent/60',
        )}
        aria-label="Switch organization"
      >
        <span className="flex min-w-0 flex-col">
          <span
            className="truncate text-sm font-semibold tracking-wide text-foreground"
            title={organizationName}
          >
            {organizationName}
          </span>

          {activeRole ? (
            <span className="truncate font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              {activeRole}
            </span>
          ) : null}
        </span>

        <ChevronsUpDown className="ml-auto h-3.5 w-3.5 shrink-0 text-muted-foreground transition-colors group-hover:text-foreground" />
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="start"
        sideOffset={6}
        className="w-60 border border-border bg-popover"
      >
        <DropdownMenuLabel className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          Switch Organization
        </DropdownMenuLabel>

        <DropdownMenuSeparator />

        {memberships.map((membership) => {
          const isActive = membership.tenant_id === tenantId

          return (
            <DropdownMenuItem
              key={membership.id}
              onClick={() => handleSelect(membership)}
              className={cn('flex items-start gap-2 py-1.5', isActive && 'bg-primary/5')}
            >
              <Check
                className={cn(
                  'mt-0.5 h-3.5 w-3.5 shrink-0',
                  isActive ? 'text-primary opacity-100' : 'opacity-0',
                )}
              />

              <span className="flex min-w-0 flex-col">
                <span
                  className={cn(
                    'truncate text-sm font-medium',
                    isActive ? 'text-primary' : 'text-foreground',
                  )}
                  title={membership.tenant_name}
                >
                  {membership.tenant_name}
                </span>

                <span className="truncate font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  {formatRole(membership.role)}
                </span>
              </span>
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
