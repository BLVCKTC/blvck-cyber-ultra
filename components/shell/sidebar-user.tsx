'use client'

import { LogOut, UserCircle } from 'lucide-react'

export type SidebarUserProps = {
  name?: string
  email?: string
  role?: string
  avatarUrl?: string
  onLogout?: () => void
}

export function SidebarUser({
  name = 'User',
  email = 'user@example.com',
  role = 'Member',
  avatarUrl,
  onLogout,
}: SidebarUserProps) {
  return (
    <div
      className="
        border-t
        border-sidebar-border
        p-4
      "
    >
      <div
        className="
          flex
          items-center
          gap-3
          rounded-lg
          p-2
          transition-colors
          hover:bg-sidebar-accent/60
        "
      >
        {/* Avatar */}
        {avatarUrl ? (
          <img
            src={avatarUrl}
            alt={name}
            loading="lazy"
            referrerPolicy="no-referrer"
            className="
              h-9
              w-9
              rounded-full
              object-cover
            "
          />
        ) : (
          <div
            className="
              flex
              h-9
              w-9
              items-center
              justify-center
              rounded-full
              bg-primary/10
              text-primary
            "
          >
            <UserCircle className="h-5 w-5" />
          </div>
        )}

        {/* User details */}
        <div
          className="
            min-w-0
            flex-1
          "
        >
          <p
            className="
              truncate
              text-sm
              font-medium
            "
          >
            {name}
          </p>

          <p
            className="
              truncate
              text-xs
              text-muted-foreground
            "
          >
            {email}
          </p>

          <span
            className="
              mt-1
              inline-flex
              rounded-md
              bg-primary/10
              px-2
              py-0.5
              text-[10px]
              font-semibold
              uppercase
              tracking-wide
              text-primary
            "
          >
            {role}
          </span>
        </div>

        {/* Logout */}
        {onLogout && (
          <button
            type="button"
            onClick={onLogout}
            className="
              rounded-md
              p-2
              text-muted-foreground
              transition-colors
              hover:bg-destructive/10
              hover:text-destructive
            "
            aria-label="Logout"
          >
            <LogOut className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}
