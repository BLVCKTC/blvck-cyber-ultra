import { cn } from '@/lib/utils'

export function GlassCard({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'glass rounded-xl p-4 shadow-lg shadow-black/20',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  title,
  sub,
  icon: Icon,
  action,
}: {
  title: string
  sub?: string
  icon?: React.ComponentType<{ className?: string }>
  action?: React.ReactNode
}) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <div className="flex items-start gap-2.5">
        {Icon && (
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/15 text-primary">
            <Icon className="h-4 w-4" />
          </div>
        )}
        <div className="leading-tight">
          <h3 className="text-sm font-semibold tracking-tight text-foreground text-balance">
            {title}
          </h3>
          {sub && <p className="mt-0.5 text-xs text-muted-foreground">{sub}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}
