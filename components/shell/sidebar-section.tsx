'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { ChevronDown } from 'lucide-react'

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'

import { cn } from '@/lib/utils'
import type { NavItem } from '@/lib/nav'

import { SidebarNavItem } from './sidebar-nav-item'

export type SidebarSectionProps = {
  title: string
  items: NavItem[]
  tenantId: string
  onNavigate?: () => void
}

export function SidebarSection({
  title,
  items,
  tenantId,
  onNavigate,
}: SidebarSectionProps) {
  const pathname = usePathname()

  const hasActiveItem = items.some((item) => pathname.startsWith(item.href))

  const [open, setOpen] = useState(hasActiveItem)

  useEffect(() => {
    if (hasActiveItem) {
      setOpen(true)
    }
  }, [hasActiveItem])

  return (
    <Collapsible open={open} onOpenChange={setOpen} className="space-y-0.5">
      <CollapsibleTrigger
        className={cn(
          `
          group
          flex
          w-full
          items-center
          justify-between
          rounded-md
          px-3
          py-1.5
          text-[11px]
          font-semibold
          uppercase
          tracking-[0.12em]
          outline-none
          `,
          `
          text-muted-foreground/70
          transition-colors
          hover:text-foreground
          focus-visible:ring-2
          focus-visible:ring-primary/40
          `,
        )}
      >
        <span className="truncate">{title}</span>

        <ChevronDown
          className={cn(
            'h-3.5 w-3.5 shrink-0 text-muted-foreground/50 transition-transform duration-200 group-hover:text-muted-foreground',
            !open && '-rotate-90',
          )}
        />
      </CollapsibleTrigger>

      <CollapsibleContent
        className="
          overflow-hidden
          data-[state=open]:animate-collapsible-down
          data-[state=closed]:animate-collapsible-up
        "
      >
        <div
          className="
            space-y-0.5
            py-0.5
            pl-1
          "
        >
          {items.map((item) => (
            <SidebarNavItem
              key={item.href}
              title={item.title}
              href={item.href}
              icon={item.icon}
              badge={item.badge}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
