"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { adminNavItems } from "@/lib/admin-nav"
import { cn } from "@/lib/utils"

export function AdminNav() {
  const pathname = usePathname()

  return (
    <nav className="flex-1 space-y-1 p-3">
      {adminNavItems.map((item) => {
        const active = pathname === item.href || pathname.startsWith(item.href + "/")

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors",
              active
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-foreground"
            )}
          >
            <item.icon className={cn("h-4 w-4", active && "text-primary")} />
            <span className="flex-1 font-medium">{item.title}</span>
            {item.badge && (
              <span className="rounded bg-primary/15 px-2 py-0.5 text-[10px] font-semibold text-primary">
                {item.badge}
              </span>
            )}
          </Link>
        )
      })}
    </nav>
  )
}
