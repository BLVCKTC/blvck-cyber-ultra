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
      aria-current={active ? 'page' : undefined}
      className={cn(
        `
        group
        relative
        flex
        items-center
        gap-3
        rounded-md
        py-2
        pl-4
        pr-2.5
        text-sm
        outline-none
        transition-colors
        duration-150
        focus-visible:ring-2
        focus-visible:ring-primary/40
        `,
        active
          ? 'bg-primary/10 text-foreground'
          : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-foreground',
      )}
    >
      {/* Active accent rail */}
      <span
        aria-hidden
        className={cn(
          'absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-primary transition-all duration-200',
          active ? 'opacity-100' : 'opacity-0 group-hover:h-3 group-hover:opacity-40',
        )}
      />

      <Icon
        className={cn(
          'h-4 w-4 shrink-0 transition-colors',
          active
            ? 'text-primary'
            : 'text-muted-foreground/80 group-hover:text-foreground',
        )}
      />

      <span className={cn('flex-1 truncate', active ? 'font-medium' : 'font-normal')}>
        {title}
      </span>

      {badge && (
        <span
          className="
            rounded
            bg-primary/15
            px-1.5
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
