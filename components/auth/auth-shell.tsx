import type { ReactNode } from 'react'
import { Shield } from 'lucide-react'

/**
 * Split-screen authentication shell.
 * Left  : authentication surface (form supplied via children)
 * Right : BLVCK Systems Africa ecosystem introduction
 *
 * The near-black + electric-blue palette is scoped locally (explicit hex) so
 * the authenticated app's existing theme tokens remain untouched.
 */
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen w-full bg-[#080A0D] text-[#E6EAF0]">
      {/* Left — authentication */}
      <div className="relative flex w-full flex-col justify-center px-6 py-12 sm:px-10 lg:w-[46%] lg:px-16">
        {/* subtle infrastructure grid + accent glow */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              'radial-gradient(circle at 20% 20%, rgba(37,99,235,0.10), transparent 42%)',
          }}
        />
        <div className="relative z-10 mx-auto w-full max-w-sm">
          {/* Brand */}
          <div className="mb-10 flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-md bg-[#11161D] ring-1 ring-[#2563EB]/40">
              <Shield className="h-4.5 w-4.5 text-[#3B82F6]" />
            </span>
            <span className="font-mono text-sm font-semibold tracking-[0.2em] text-[#E6EAF0]">
              BLVCK <span className="text-[#3B82F6]">CYBER</span>
            </span>
          </div>

          {children}
        </div>
      </div>

      {/* Right — ecosystem */}
      <EcosystemPanel />
    </div>
  )
}

function EcosystemPanel() {
  return (
    <aside
      className="relative hidden overflow-hidden border-l border-white/5 lg:flex lg:w-[54%] lg:flex-col lg:justify-between"
      style={{
        background:
          'linear-gradient(160deg, #0D1117 0%, #0A0D12 60%, #080A0D 100%)',
      }}
    >
      {/* accent field */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(circle at 80% 20%, rgba(37,99,235,0.14), transparent 40%)',
        }}
      />
      {/* faint grid */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.5]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
          backgroundSize: '52px 52px',
          maskImage:
            'radial-gradient(circle at 70% 30%, black, transparent 75%)',
        }}
      />

      <div className="relative z-10 px-16 pt-16">
        <p className="font-mono text-xs tracking-[0.32em] text-[#5B6472]">
          BLVCK SYSTEMS AFRICA
        </p>
        <h2 className="mt-6 max-w-md text-3xl font-semibold leading-tight text-balance text-[#E6EAF0]">
          Building the infrastructure behind Africa&apos;s digital future.
        </h2>
      </div>

      <div className="relative z-10 px-16">
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-semibold tracking-wide text-[#E6EAF0]">
            BLVCK ONE
          </span>
          <span className="font-mono text-xs text-[#3B82F6]">™</span>
        </div>
        <p className="mt-2 max-w-sm text-sm leading-relaxed text-[#8A93A3]">
          One ecosystem. Connected intelligence. Built for scale.
        </p>

        {/* ecosystem tree */}
        <div className="mt-8 space-y-2.5">
          <EcosystemNode label="BLVCK ONE" root />
          <EcosystemNode label="BLVCK CYBER" active />
          <EcosystemNode label="BLVCK INTELLIGENCE" />
          <EcosystemNode label="BLVCK CLOUD" />
          <EcosystemNode label="Industry Platforms" last />
        </div>
      </div>

      <div className="relative z-10 flex items-center gap-4 px-16 pb-16 pt-12">
        {['CYBER', 'INTELLIGENCE', 'CLOUD', 'INDUSTRY'].map((tag, i) => (
          <div key={tag} className="flex items-center gap-4">
            {i > 0 && <span className="h-1 w-1 rounded-full bg-[#2563EB]/60" />}
            <span className="font-mono text-[11px] tracking-[0.22em] text-[#5B6472]">
              {tag}
            </span>
          </div>
        ))}
      </div>
    </aside>
  )
}

function EcosystemNode({
  label,
  root = false,
  active = false,
  last = false,
}: {
  label: string
  root?: boolean
  active?: boolean
  last?: boolean
}) {
  if (root) {
    return (
      <div className="flex items-center gap-3">
        <span className="h-2 w-2 rounded-full bg-[#3B82F6]" />
        <span className="font-mono text-xs tracking-[0.18em] text-[#E6EAF0]">
          {label}
        </span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 pl-1">
      {/* connector */}
      <span className="relative flex h-5 w-4 items-center">
        <span className="absolute left-0 top-0 h-1/2 w-px bg-white/10" />
        {!last && (
          <span className="absolute left-0 top-1/2 h-1/2 w-px bg-white/10" />
        )}
        <span className="absolute left-0 top-1/2 h-px w-3 bg-white/10" />
      </span>
      <span
        className={
          active
            ? 'font-mono text-xs tracking-[0.14em] text-[#3B82F6]'
            : 'font-mono text-xs tracking-[0.14em] text-[#8A93A3]'
        }
      >
        {label}
      </span>
    </div>
  )
}
