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
    <Collapsible open={open} onOpenChange={setOpen} className="space-y-1">
      <CollapsibleTrigger
        className={cn(
          `
          group
          flex
          w-full
          items-center
          justify-between
          rounded-lg
          px-3
          py-2
          text-xs
          font-semibold
          uppercase
          tracking-wide
          `,
          `
          text-muted-foreground
          transition-colors
          hover:bg-sidebar-accent/60
          hover:text-foreground
          `,
        )}
      >
        <span>{title}</span>

        <ChevronDown
          className={cn(
            'h-4 w-4 transition-transform duration-200',
            open && 'rotate-180',
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
            ml-2
            space-y-1
            border-l
            border-sidebar-border
            pl-3
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
