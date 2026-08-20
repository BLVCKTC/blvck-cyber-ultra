import type { ReactNode } from 'react'
import { ArrowUpRight, Shield, Terminal } from 'lucide-react'

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

      <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-5 py-8 sm:px-8 lg:px-12">
        <div className="grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-border/70 bg-card/80 shadow-2xl shadow-background/60 backdrop-blur-xl lg:grid-cols-[0.78fr_1.22fr]">
          <section className="order-2 flex flex-col justify-between gap-10 bg-card p-7 sm:p-10 lg:order-1 lg:min-h-[34rem] lg:p-12">
            <div className="flex items-center gap-3">
              <span className="flex size-9 items-center justify-center rounded-xl border border-primary/30 bg-primary/10 text-primary">
                <Shield aria-hidden className="size-4" />
              </span>
              <span className="font-mono text-xs font-semibold tracking-[0.22em]">
                BLVCK <span className="text-primary">CYBER</span>
              </span>
            </div>
            {children}
            <div className="flex items-center justify-between gap-4 font-mono text-[9px] uppercase tracking-[0.14em] text-muted-foreground">
              <span>Private by design</span>
              <span>© 2026</span>
            </div>
          </section>

          <section className="relative order-1 flex min-h-[18rem] flex-col justify-between overflow-hidden bg-primary p-7 text-primary-foreground sm:p-10 lg:order-2 lg:min-h-[34rem] lg:p-12">
            <div
              aria-hidden
              className="absolute inset-0 bg-cover bg-center opacity-75 mix-blend-multiply"
              style={{
                backgroundImage:
                  "url('https://hebbkx1anhila5yf.public.blob.vercel-storage.com/pros-and-cons-scaled-2560x1280-NFKc0AGXh8GHMA8B6ndFSL4kjqAX43.jpeg')",
              }}
            />
            <div aria-hidden className="absolute inset-0 bg-primary/35" />
            <div aria-hidden className="absolute -right-24 -top-24 size-72 rounded-full border border-primary-foreground/20" />
            <div aria-hidden className="absolute -bottom-40 -left-24 size-96 rounded-full border border-primary-foreground/10" />
            <div className="relative flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.16em] opacity-70">
              <span>BLVCK ID</span>
              <span className="flex items-center gap-1.5">Online <span className="size-1.5 rounded-full bg-current" /></span>
            </div>
            <div className="relative max-w-md">
              <p className="mb-5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] opacity-70">
                <Terminal aria-hidden className="size-3.5" />
                Security operations platform
              </p>
              <h1 className="text-balance text-5xl font-semibold tracking-[-0.07em] sm:text-6xl lg:text-7xl">
                Welcome.
              </h1>
              <p className="mt-5 max-w-sm text-pretty text-sm leading-6 opacity-75 sm:text-base">
                See what matters. Respond with confidence. Your security environment is ready when you are.
              </p>
            </div>
            <div className="relative flex items-center justify-between gap-4 border-t border-primary-foreground/20 pt-5 font-mono text-[9px] uppercase tracking-[0.14em] opacity-70">
              <span>Encrypted access</span>
              <ArrowUpRight aria-hidden className="size-4" />
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}
