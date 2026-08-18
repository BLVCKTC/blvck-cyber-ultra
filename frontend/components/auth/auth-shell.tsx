import type { ReactNode } from 'react'
import { Shield } from 'lucide-react'

import { EcosystemPanel } from './ecosystem-panel'

/**
 * Split-screen authentication shell shared by /login and /signup.
 *
 * Desktop : two columns — authentication surface (~44%) on the left,
 *           the BLVCK Systems Africa / BLVCK ONE ecosystem panel (~56%) right.
 * Mobile  : stacks vertically — authentication first, ecosystem below (the
 *           ecosystem message is never fully hidden).
 *
 * The near-black + electric-blue palette is scoped locally (explicit hex) so
 * the authenticated app's existing theme tokens remain untouched.
 */
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen w-full flex-col bg-[#080A0D] text-[#E6EAF0] lg:flex-row">
      {/* Left — authentication */}
      <div className="relative flex w-full flex-col justify-center px-6 py-12 sm:px-10 lg:w-[44%] lg:px-16">
        {/* subtle accent glow */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              'radial-gradient(circle at 20% 20%, rgba(37,99,235,0.10), transparent 42%)',
          }}
        />
        <div className="relative z-10 mx-auto flex w-full max-w-sm flex-col">
          {/* Brand */}
          <div className="mb-10 flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-md bg-[#11161D] ring-1 ring-[#2563EB]/40">
              <Shield className="h-[18px] w-[18px] text-[#3B82F6]" />
            </span>
            <span className="font-mono text-sm font-semibold tracking-[0.2em] text-[#E6EAF0]">
              BLVCK <span className="text-[#3B82F6]">CYBER</span>
            </span>
          </div>

          {children}
        </div>
      </div>

      {/* Right (desktop) / below (mobile) — ecosystem */}
      <div className="w-full lg:w-[56%]">
        <EcosystemPanel />
      </div>
    </div>
  )
}
