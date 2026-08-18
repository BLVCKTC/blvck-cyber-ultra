import type { ReactNode } from "react"
import type { LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"

type PageHeaderProps = {
  icon?: LucideIcon
  eyebrow?: string
  title: string
  description?: string
  actions?: ReactNode
  className?: string
}

export function PageHeader({
  icon: Icon,
  eyebrow,
  title,
  description,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4 border-b border-border px-4 py-6 sm:flex-row sm:items-end sm:justify-between lg:px-6",
        className
      )}
    >
      <div className="flex min-w-0 items-start gap-4">
        {Icon && (
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-primary/20 bg-primary/10 shadow-sm">
            <Icon className="h-7 w-7 text-primary" />
          </div>
        )}

        <div className="min-w-0">
          {eyebrow && (
            <div className="mb-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              {eyebrow}
            </div>
          )}

          <h1 className="font-display text-2xl font-bold tracking-tight text-foreground text-balance">
            {title}
          </h1>

          {description && (
            <p className="mt-1.5 max-w-2xl text-pretty text-sm leading-relaxed text-muted-foreground">
              {description}
            </p>
          )}
        </div>
      </div>

      {actions && (
        <div className="flex shrink-0 items-center gap-2">
          {actions}
        </div>
      )}
    </div>
  )
}