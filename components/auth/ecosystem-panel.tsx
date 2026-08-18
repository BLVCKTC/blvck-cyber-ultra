import { Shield, BrainCircuit, Cloud, Layers } from 'lucide-react'

/**
 * Right-hand ecosystem panel for the authentication experience.
 *
 * Presents BLVCK SYSTEMS AFRICA (the company) and BLVCK ONE™ (the ecosystem
 * layer), with BLVCK CYBER visually emphasized because it is the product the
 * user is signing in to. Restrained enterprise language: near-black surface,
 * a single electric-blue accent, thin borders, subtle radial lighting — no
 * neon, no animated gradients, no decorative filler.
 *
 * Rendered both as the desktop right column and, stacked, below the login
 * panel on mobile (so the ecosystem message is never fully hidden).
 */
export function EcosystemPanel() {
  return (
    <aside
      className="relative flex flex-col justify-between overflow-hidden border-t border-white/5 px-8 py-14 lg:border-l lg:border-t-0 lg:px-16 lg:py-16"
      style={{
        background:
          'linear-gradient(160deg, #0D1117 0%, #0A0D12 60%, #080A0D 100%)',
      }}
    >
      {/* subtle radial lighting behind the visualization */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(circle at 82% 22%, rgba(37,99,235,0.13), transparent 45%)',
        }}
      />
      {/* faint infrastructure grid, softly masked */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
          backgroundSize: '52px 52px',
          maskImage:
            'radial-gradient(circle at 72% 28%, black, transparent 78%)',
          WebkitMaskImage:
            'radial-gradient(circle at 72% 28%, black, transparent 78%)',
        }}
      />

      {/* Company positioning */}
      <div className="relative z-10">
        <p className="font-mono text-xs tracking-[0.32em] text-[#5B6472]">
          BLVCK SYSTEMS AFRICA
        </p>
        <h2 className="mt-6 max-w-lg text-2xl font-semibold leading-tight text-balance text-[#E6EAF0] lg:text-[1.9rem]">
          Building the intelligence and security infrastructure for
          Africa&apos;s digital future.
        </h2>
        <p className="mt-4 max-w-md text-sm leading-relaxed text-pretty text-[#8A93A3]">
          BLVCK Systems Africa is building a connected technology ecosystem for
          the next generation of African enterprises — combining cybersecurity,
          intelligence, cloud infrastructure and industry-specific platforms.
        </p>
      </div>

      {/* Ecosystem layer */}
      <div className="relative z-10 mt-12 lg:mt-0">
        <div className="flex items-baseline gap-1.5">
          <span className="text-xl font-semibold tracking-wide text-[#E6EAF0]">
            BLVCK ONE
          </span>
          <span className="font-mono text-xs text-[#3B82F6]">™</span>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-[#8A93A3]">
          One ecosystem. Connected intelligence. Built for scale.
        </p>

        {/* Ecosystem visualization — clean vertical system with connectors */}
        <div className="mt-8 max-w-md">
          <RootNode />
          <div className="mt-1.5 space-y-1.5">
            <BranchNode
              icon={<Shield className="h-4 w-4" />}
              title="BLVCK CYBER"
              subtitle="Security & Digital Risk"
              active
            />
            <BranchNode
              icon={<BrainCircuit className="h-4 w-4" />}
              title="BLVCK INTELLIGENCE"
              subtitle="AI, Data & Decision Intelligence"
            />
            <BranchNode
              icon={<Cloud className="h-4 w-4" />}
              title="BLVCK CLOUD"
              subtitle="Infrastructure & Compute"
            />
            <BranchNode
              icon={<Layers className="h-4 w-4" />}
              title="Industry Platforms"
              subtitle="Mining · FinTech · Enterprise"
              last
            />
          </div>
        </div>
      </div>

      {/* Foundation statement */}
      <div className="relative z-10 mt-12 lg:mt-0">
        <p className="max-w-md border-l border-[#2563EB]/40 pl-4 text-sm leading-relaxed text-[#8A93A3]">
          BLVCK CYBER is the security intelligence foundation of the BLVCK
          ecosystem.
        </p>
      </div>
    </aside>
  )
}

function RootNode() {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-2.5 w-2.5 items-center justify-center">
        <span className="h-2.5 w-2.5 rounded-full bg-[#3B82F6] shadow-[0_0_0_4px_rgba(37,99,235,0.15)]" />
      </span>
      <span className="font-mono text-xs tracking-[0.18em] text-[#E6EAF0]">
        BLVCK ONE
      </span>
    </div>
  )
}

function BranchNode({
  icon,
  title,
  subtitle,
  active = false,
  last = false,
}: {
  icon: React.ReactNode
  title: string
  subtitle: string
  active?: boolean
  last?: boolean
}) {
  return (
    <div className="flex items-stretch gap-3">
      {/* connector rail */}
      <span aria-hidden className="relative flex w-2.5 shrink-0 justify-center">
        <span className="absolute left-1/2 top-0 h-1/2 w-px -translate-x-1/2 bg-white/10" />
        {!last && (
          <span className="absolute left-1/2 top-1/2 h-1/2 w-px -translate-x-1/2 bg-white/10" />
        )}
        <span className="absolute left-1/2 top-1/2 h-px w-2.5 bg-white/10" />
      </span>

      <div
        className={
          active
            ? 'flex flex-1 items-center gap-3 rounded-lg border border-[#2563EB]/40 bg-[#2563EB]/10 px-3.5 py-2.5 transition-colors'
            : 'flex flex-1 items-center gap-3 rounded-lg border border-white/5 bg-white/[0.02] px-3.5 py-2.5 transition-colors hover:border-white/10'
        }
      >
        <span
          className={
            active
              ? 'flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-[#2563EB]/20 text-[#3B82F6]'
              : 'flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-white/5 text-[#8A93A3]'
          }
        >
          {icon}
        </span>
        <span className="min-w-0">
          <span
            className={
              active
                ? 'flex items-center gap-2 font-mono text-xs tracking-[0.12em] text-[#E6EAF0]'
                : 'font-mono text-xs tracking-[0.12em] text-[#C3CAD5]'
            }
          >
            {title}
            {active && (
              <span className="rounded-sm bg-[#2563EB]/25 px-1.5 py-0.5 text-[9px] font-medium tracking-[0.1em] text-[#93B4FF]">
                CURRENT
              </span>
            )}
          </span>
          <span className="mt-0.5 block truncate text-xs text-[#5B6472]">
            {subtitle}
          </span>
        </span>
      </div>
    </div>
  )
}
