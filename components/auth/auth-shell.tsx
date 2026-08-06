import Link from "next/link"
import { ShieldHalf } from "lucide-react"
import type { ReactNode } from "react"

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle: string
  children: ReactNode
}) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4 py-12">
      {/* particle/grid background */}
      <div className="cyber-grid pointer-events-none absolute inset-0 opacity-40" />
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[120px]" />

      <div className="relative z-10 w-full max-w-md">
        <Link href="/" className="mb-8 flex items-center justify-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg border border-primary/40 bg-primary/10 text-primary glow-primary">
            <ShieldHalf className="h-5 w-5" />
          </span>
          <span className="font-mono text-sm font-bold tracking-wider text-foreground">
            BLVCK<span className="text-primary">CYBER</span>
          </span>
        </Link>

        <div className="rounded-xl border border-border/60 bg-card/60 p-6 backdrop-blur-xl sm:p-8">
          <div className="mb-6 text-center">
            <h1 className="font-display text-2xl font-bold text-foreground">{title}</h1>
            <p className="mt-1.5 text-sm text-muted-foreground">{subtitle}</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  )
}
