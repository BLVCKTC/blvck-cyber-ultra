'use client'

import { Shield, X } from 'lucide-react'

import { cn } from '@/lib/utils'

export type SidebarHeaderProps = {
  mobile?: boolean
  onClose?: () => void
}

export function SidebarHeader({ mobile = false, onClose }: SidebarHeaderProps) {
  return (
    <div
      className={cn(
        'flex h-16 items-center justify-between px-4',
        'border-b border-sidebar-border',
      )}
    >
      {/* Brand */}
      <div
        className="
          flex
          items-center
          gap-3
        "
      >
        <div
          className="
            flex
            h-9
            w-9
            items-center
            justify-center
            rounded-lg
            bg-primary/10
            ring-1
            ring-primary/20
          "
        >
          <Shield
            className="
              h-5
              w-5
              text-primary
            "
          />
        </div>

        <div
          className="
            flex
            flex-col
          "
        >
          <span
            className="
              text-sm
              font-bold
              tracking-wide
            "
          >
            BLVCK CYBER
          </span>

          <span
            className="
              text-[10px]
              uppercase
              tracking-widest
              text-muted-foreground
            "
          >
            Security Platform
          </span>
        </div>
      </div>

      {/* Mobile close button */}
      {mobile && (
        <button
          type="button"
          onClick={onClose}
          className="
            rounded-md
            p-2
            text-muted-foreground
            transition-colors
            hover:bg-sidebar-accent
            hover:text-foreground
          "
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  )
}
