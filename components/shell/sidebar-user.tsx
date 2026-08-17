'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  ChevronsUpDown,
  LogOut,
  Settings,
  ShieldCheck,
  UserRound,
} from 'lucide-react'

import { useAuth } from '@/lib/auth-session'
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
  const initials = initialsFrom(name, email)

  async function handleConfirmSignOut() {
    setSigningOut(true)
    // Uses the existing auth session: clears local state, performs the
    // backend/Keycloak logout, and redirects to /login.
    await logout()
  }

  return (
    <div className="border-t border-sidebar-border p-3">
      <DropdownMenu>
        <DropdownMenuTrigger className="flex w-full items-center gap-3 rounded-lg p-2 text-left transition-colors hover:bg-sidebar-accent/60">
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

        <DropdownMenuContent
          side="top"
          align="start"
          className="w-[248px]"
        >
          <DropdownMenuLabel className="flex flex-col gap-0.5">
            <span className="truncate text-sm font-medium">{name}</span>
            <span className="truncate text-xs font-normal text-muted-foreground">
              {role}
            </span>
          </DropdownMenuLabel>

          <DropdownMenuSeparator />

          <DropdownMenuItem onClick={() => router.push('/dashboard/profile')}>
            <UserRound className="h-4 w-4" />
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => router.push('/dashboard/settings/account')}
          >
            <Settings className="h-4 w-4" />
            Account Settings
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => router.push('/dashboard/settings/security')}
          >
            <ShieldCheck className="h-4 w-4" />
            Security Settings
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            variant="destructive"
            onClick={() => setConfirmOpen(true)}
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Sign-out confirmation */}
      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Sign out?</DialogTitle>
            <DialogDescription>
              You will be signed out of your BLVCK CYBER security environment.
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
              className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-destructive px-4 text-sm font-medium text-white transition-colors hover:bg-destructive/90 disabled:opacity-50"
            >
              {signingOut && (
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              )}
              Sign out
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
