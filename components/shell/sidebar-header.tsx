'use client'

import { Shield, X } from 'lucide-react'

import { cn } from '@/lib/utils'
import { TenantSwitcher } from '@/components/soc/tenant-switcher'

export type SidebarHeaderProps = {
  mobile?: boolean
  onClose?: () => void
}

export function SidebarHeader({ mobile = false, onClose }: SidebarHeaderProps) {
  return (
    <div
      className={cn(
        'flex flex-col gap-3 px-4 py-3',
        'border-b border-sidebar-border',
      )}
    >
      {/* Brand */}
      <div className="flex items-center justify-between">
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
              shrink-0
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

          <span
            className="
              text-sm
              font-bold
              tracking-wide
            "
          >
            BLVCK CYBER
          </span>
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

      {/* Active tenant / organization switcher */}
      <TenantSwitcher />
    </div>
  )
}
