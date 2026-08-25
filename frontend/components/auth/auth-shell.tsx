import { useEffect, useState, type ReactNode } from 'react'
import { ArrowUpRight, Shield, Terminal } from 'lucide-react'

/**
 * Full-bleed authentication shell shared by /login and /signup.
 * The supplied cybersecurity image provides the visual anchor while the
 * content remains a responsive, readable glass surface above it.
 */
export function AuthShell({
  children,
  animateHero = false,
}: {
  children: ReactNode
  animateHero?: boolean
}) {
  const welcomeText = 'Welcome.'
  const descriptionText = 'See what matters. Respond with confidence. Your security environment is ready when you are.'
  const [welcome, setWelcome] = useState(animateHero ? '' : welcomeText)
  const [description, setDescription] = useState(animateHero ? '' : descriptionText)

  useEffect(() => {
    if (!animateHero) return
    let index = 0
    const welcomeTimer = window.setInterval(() => {
      index += 1
      setWelcome(welcomeText.slice(0, index))
      if (index >= welcomeText.length) window.clearInterval(welcomeTimer)
    }, 110)

    const descriptionTimer = window.setTimeout(() => {
      let descriptionIndex = 0
      const timer = window.setInterval(() => {
        descriptionIndex += 1
        setDescription(descriptionText.slice(0, descriptionIndex))
        if (descriptionIndex >= descriptionText.length) window.clearInterval(timer)
      }, 22)
    }, welcomeText.length * 110 + 260)

    return () => {
      window.clearInterval(welcomeTimer)
      window.clearTimeout(descriptionTimer)
    }
  }, [animateHero])

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
      <div aria-hidden className="absolute inset-0 -z-10 bg-sidebar/90" />
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-[linear-gradient(90deg,hsl(var(--sidebar)/.98)_0%,hsl(var(--sidebar)/.84)_45%,hsl(var(--sidebar)/.42)_100%)]"
      />

      <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-5 py-8 sm:px-8 lg:px-12">
        <div className="grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-border/70 bg-card/80 shadow-2xl shadow-background/60 backdrop-blur-xl lg:grid-cols-[0.78fr_1.22fr]">
          <section className="order-2 flex flex-col justify-between gap-10 bg-sidebar p-7 text-sidebar-foreground sm:p-10 lg:order-1 lg:min-h-[34rem] lg:p-12">
            <div className="flex items-center gap-3">
              <span className="flex size-9 items-center justify-center rounded-xl border border-sidebar-primary/30 bg-sidebar-primary/10 text-sidebar-primary">
                <Shield aria-hidden className="size-4" />
              </span>
              <span className="font-mono text-xs font-semibold tracking-[0.22em]">
                BLVCK <span className="text-sidebar-primary">CYBER</span>
              </span>
            </div>
            {children}
            <div className="flex items-center justify-between gap-4 font-mono text-[9px] uppercase tracking-[0.14em] text-muted-foreground">
              <span>Private by design</span>
              <span>© 2026</span>
            </div>
          </section>

          <section className="relative order-1 flex min-h-[18rem] flex-col justify-between overflow-hidden bg-background p-7 text-foreground sm:p-10 lg:order-2 lg:min-h-[34rem] lg:p-12">
            <div
              aria-hidden
              className="absolute inset-0 bg-cover bg-center"
              style={{
                backgroundImage:
                  "url('https://hebbkx1anhila5yf.public.blob.vercel-storage.com/pros-and-cons-scaled-2560x1280-NFKc0AGXh8GHMA8B6ndFSL4kjqAX43.jpeg')",
              }}
            />
            <div className="relative flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.16em] text-sidebar-foreground/85">
              <span>BLVCK ID</span>
              <span className="flex items-center gap-1.5">Online <span className="size-1.5 rounded-full bg-current" /></span>
            </div>
            <div className="relative max-w-md">
              <p className="mb-5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-sidebar-foreground/80">
                <Terminal aria-hidden className="size-3.5" />
                Security operations platform
              </p>
              <h1 className="text-balance text-5xl font-semibold tracking-[-0.07em] text-sidebar-primary sm:text-6xl lg:text-7xl">
                {welcome}
                {animateHero && welcome.length < welcomeText.length && <span aria-hidden className="ml-1 animate-pulse">|</span>}
              </h1>
              <p className="mt-5 max-w-sm text-pretty text-sm leading-6 text-sidebar-primary/90 sm:text-base">
                {description}
                {animateHero && welcome.length === welcomeText.length && description.length < descriptionText.length && <span aria-hidden className="ml-0.5 animate-pulse">|</span>}
              </p>
            </div>
            <div className="relative flex items-center justify-between gap-4 border-t border-sidebar-foreground/30 pt-5 font-mono text-[9px] uppercase tracking-[0.14em] text-sidebar-foreground/80">
              <span>Encrypted access</span>
              <ArrowUpRight aria-hidden className="size-4" />
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}
