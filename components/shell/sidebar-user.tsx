'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Building2,
  ChevronsUpDown,
  LogOut,
  ShieldCheck,
  UserRound,
} from 'lucide-react'

import { useAuth } from '@/lib/auth-session'
import { useTenant } from '@/components/providers/tenant-provider'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'

export type SidebarUserProps = {
  /** Optional fallbacks used until the authenticated session resolves. */
  name?: string
  email?: string
  role?: string
  avatarUrl?: string
  /** Retained for backwards compatibility; sign-out uses the auth session. */
  onLogout?: () => void
}

function initialsFrom(name: string, email: string) {
  const source = name?.trim() || email?.trim() || 'User'
  const parts = source.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return source.slice(0, 2).toUpperCase()
}

function humanizeRole(role: string) {
  if (!role) return 'Member'
  return role
    .replace(/[_-]+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

export function SidebarUser({
  name: nameProp,
  email: emailProp,
  role: roleProp,
  avatarUrl,
}: SidebarUserProps) {
  const router = useRouter()
  const { user, memberships, activeTenant, logout } = useAuth()
  const { tenantId, organizationName } = useTenant()

  const [confirmOpen, setConfirmOpen] = useState(false)
  const [signingOut, setSigningOut] = useState(false)

  // Prefer authenticated session data; fall back to props for first paint.
  const name = user?.name || nameProp || 'User'
  const email = user?.email || emailProp || ''

  const activeMembership =
    memberships.find((m) => m.tenant_id === activeTenant) ??
    memberships.find((m) => m.is_default) ??
    memberships[0]

  const role = humanizeRole(activeMembership?.role || roleProp || 'Member')
  const organization = organizationName || activeTenant || 'BLVCK CYBER'
  const initials = initialsFrom(name, email)

  async function handleConfirmSignOut() {
    setSigningOut(true)
    // Clears client-side auth state and hands off to the backend/Keycloak
    // redirect-based logout, which ends back on /login (see auth-session).
    await logout()
  }

  return (
    <div className="border-t border-sidebar-border p-3">
      <DropdownMenu>
        <DropdownMenuTrigger className="flex w-full items-center gap-3 rounded-lg p-2 text-left transition-colors hover:bg-sidebar-accent/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40">
          {/* Avatar */}
          {avatarUrl ? (
            <img
              src={avatarUrl || '/placeholder.svg'}
              alt=""
              loading="lazy"
              referrerPolicy="no-referrer"
              className="h-9 w-9 shrink-0 rounded-full object-cover"
            />
          ) : (
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
              {initials}
            </span>
          )}

          {/* Identity */}
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-medium text-foreground">
              {name}
            </span>
            <span className="block truncate text-xs text-muted-foreground">
              {role}
            </span>
          </span>

          {/* Online status + affordance */}
          <span className="flex flex-col items-center gap-1">
            <span
              className="h-2 w-2 rounded-full bg-success"
              aria-label="Online"
            />
            <ChevronsUpDown className="h-3.5 w-3.5 text-muted-foreground" />
          </span>
        </DropdownMenuTrigger>

        <DropdownMenuContent side="top" align="start" className="w-[264px]">
          {/* Rich identity block: name, email, organization, role */}
          <DropdownMenuLabel className="flex items-center gap-3 py-2.5">
            {avatarUrl ? (
              <img
                src={avatarUrl || '/placeholder.svg'}
                alt=""
                className="h-9 w-9 shrink-0 rounded-full object-cover"
              />
            ) : (
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
                {initials}
              </span>
            )}
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium text-foreground">
                {name}
              </span>
              {email && (
                <span className="block truncate text-xs font-normal text-muted-foreground">
                  {email}
                </span>
              )}
            </span>
          </DropdownMenuLabel>

          <div className="px-2 pb-2">
            <div className="flex items-center justify-between gap-2 rounded-md bg-sidebar-accent/40 px-2.5 py-1.5">
              <span className="flex min-w-0 items-center gap-1.5 text-xs text-muted-foreground">
                <Building2 className="h-3.5 w-3.5 shrink-0 text-primary/70" />
                <span className="truncate">{organization}</span>
              </span>
              <span className="shrink-0 rounded-sm bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-primary">
                {role}
              </span>
            </div>
          </div>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            onClick={() => router.push(`/dashboard/${tenantId}/settings`)}
          >
            <UserRound className="h-4 w-4" />
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => router.push(`/dashboard/${tenantId}/mfa`)}
          >
            <ShieldCheck className="h-4 w-4" />
            Security
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => router.push(`/dashboard/${tenantId}/organization`)}
          >
            <Building2 className="h-4 w-4" />
            Organization
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            onClick={() => setConfirmOpen(true)}
            className="text-amber-600 focus:bg-amber-500/10 focus:text-amber-600 dark:text-amber-400 dark:focus:text-amber-400"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Sign-out confirmation */}
      <Dialog
        open={confirmOpen}
        onOpenChange={(open) => {
          // Don't allow dismissing the dialog while the sign-out redirect runs.
          if (!signingOut) setConfirmOpen(open)
        }}
      >
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Sign out?</DialogTitle>
            <DialogDescription>
              You&apos;ll be signed out of your BLVCK CYBER security environment
              and returned to the sign-in screen.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <button
              type="button"
              onClick={() => setConfirmOpen(false)}
              disabled={signingOut}
              className="inline-flex h-9 items-center justify-center rounded-md border border-border px-4 text-sm font-medium text-foreground transition-colors hover:bg-accent disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirmSignOut}
              disabled={signingOut}
              className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-amber-600 px-4 text-sm font-medium text-white transition-colors hover:bg-amber-600/90 disabled:opacity-70"
            >
              {signingOut && (
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              )}
              {signingOut ? 'Signing you out…' : 'Sign out'}
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
