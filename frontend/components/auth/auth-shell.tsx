import type { ReactNode } from 'react'
import { Shield, Terminal } from 'lucide-react'

/**
 * Full-bleed authentication shell shared by /login and /signup.
 * The supplied cybersecurity image provides the visual anchor while the
 * content remains a responsive, readable glass surface above it.
 */
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <main className="relative isolate flex min-h-screen w-full overflow-hidden bg-background text-foreground">
      <div
        aria-hidden
        className="absolute inset-0 -z-20 bg-cover bg-center"
        style={{
          backgroundImage:
            "url('https://hebbkx1anhila5yf.public.blob.vercel-storage.com/1696886816239-2VFwEjWK9MEpCIfklLjJ4AtEyy2pgD.jpg')",
        }}
      />
      <div aria-hidden className="absolute inset-0 -z-10 bg-background/80" />
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-[linear-gradient(90deg,hsl(var(--background)/.96)_0%,hsl(var(--background)/.78)_45%,hsl(var(--background)/.38)_100%)]"
      />
      <div aria-hidden className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_78%_45%,hsl(var(--primary)/.16),transparent_34%)]" />

      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col justify-between gap-12 px-6 py-8 sm:px-10 lg:flex-row lg:items-center lg:gap-16 lg:px-16 lg:py-12">
        <section className="flex max-w-xl flex-col justify-between gap-12 lg:min-h-[34rem]">
          <div className="flex items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-xl border border-primary/30 bg-primary/10 text-primary shadow-[0_0_32px_hsl(var(--primary)/.18)]">
              <Shield aria-hidden className="size-5" />
            </span>
            <span className="font-mono text-sm font-semibold tracking-[0.24em]">
              BLVCK <span className="text-primary">CYBER</span>
            </span>
          </div>

          <div className="max-w-lg">
            <p className="mb-5 flex items-center gap-2 font-mono text-xs uppercase tracking-[0.24em] text-primary">
              <Terminal aria-hidden className="size-3.5" />
              Security operations platform
            </p>
            <h1 className="max-w-xl text-balance text-5xl font-semibold tracking-[-0.06em] sm:text-6xl lg:text-7xl">
              Welcome back.
            </h1>
            <p className="mt-6 max-w-md text-pretty text-base leading-7 text-muted-foreground sm:text-lg">
              See what matters. Respond with confidence. Your security environment is ready when you are.
            </p>
          </div>

          <div className="flex flex-wrap gap-x-6 gap-y-2 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
            <span>BLVCK ID</span>
            <span>Encrypted access</span>
            <span>© 2026 BLVCK SYSTEMS</span>
          </div>
        </section>

        <section className="w-full max-w-md rounded-3xl border border-border/70 bg-card/80 p-6 shadow-2xl shadow-background/40 backdrop-blur-xl sm:p-8 lg:p-10">
          {children}
        </section>
      </div>
    </main>
  )
}
