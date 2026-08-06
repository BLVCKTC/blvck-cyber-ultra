'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type { LucideIcon } from 'lucide-react'

import { cn } from '@/lib/utils'

export type SidebarNavItemProps = {
  title: string
  href: string
  icon: LucideIcon
  onNavigate?: () => void
  badge?: string
}

export function SidebarNavItem({
  title,
  href,
  icon: Icon,
  onNavigate,
  badge,
}: SidebarNavItemProps) {
  const pathname = usePathname()

  const active = pathname === href || pathname.startsWith(`${href}/`)

  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        `
        group
        flex
        items-center
        gap-3
        rounded-lg
        px-3
        py-2
        text-sm
        transition-all
        duration-200
        `,
        active
          ? `
            bg-sidebar-accent
            text-sidebar-accent-foreground
            shadow-sm
          `
          : `
            text-muted-foreground
            hover:bg-sidebar-accent/60
            hover:text-foreground
          `,
      )}
    >
      <Icon
        className={cn(
          'h-4 w-4 shrink-0',
          active ? 'text-primary' : 'group-hover:text-primary',
        )}
      />

      <span className="flex-1 truncate font-medium">{title}</span>

      {badge && (
        <span
          className="
            rounded-md
            bg-primary/15
            px-2
            py-0.5
            text-[10px]
            font-semibold
            uppercase
            tracking-wide
            text-primary
          "
        >
          {badge}
        </span>
      )}
    </Link>
  )
}
