import type React from "react"
import { cn } from "@/lib/utils"

interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  icon?: React.ReactNode
  action?: React.ReactNode
  bodyClassName?: string
}

export function Panel({ title, icon, action, children, className, bodyClassName, ...props }: PanelProps) {
  return (
    <section
      className={cn(
        "flex flex-col rounded-lg border border-border bg-card/60 backdrop-blur-sm",
        className,
      )}
      {...props}
    >
      {title && (
        <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-3">
          <div className="flex items-center gap-2">
            {icon && <span className="text-primary">{icon}</span>}
            <h2 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">{title}</h2>
          </div>
          {action}
        </header>
      )}
      <div className={cn("flex-1 p-4", bodyClassName)}>{children}</div>
    </section>
  )
}
