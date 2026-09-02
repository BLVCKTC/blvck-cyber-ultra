'use client'

import Link from 'next/link'
import { Crosshair } from 'lucide-react'
import { useEffect, useState } from 'react'

import { Panel } from '@/components/soc/panel'
import { API_URL, authenticatedFetch } from '@/lib/api/client'

type MitreCoverageProps = {
  tenantId: string
}

type CoverageResponse = {
  covered: number
  uncovered: number
  total?: number
}

export function MitreCoverage({ tenantId }: MitreCoverageProps) {
  const [coverage, setCoverage] = useState<CoverageResponse>({
    covered: 0,
    uncovered: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    async function loadCoverage() {
      try {
        const response = await authenticatedFetch(
          `${API_URL}/v1/tenants/${tenantId}/mitre/coverage`,
          {
            signal: controller.signal,
            cache: 'no-store',
          },
        )

        if (!response.ok) {
          throw new Error('Failed to load MITRE coverage')
        }

        const result = await response.json()
        const data = result.data ?? result

        setCoverage({
          covered: data.covered ?? data.covered_techniques ?? 0,
          uncovered: data.uncovered ?? data.uncovered_techniques ?? 0,
          total:
            data.total ??
            data.total_techniques ??
            (data.covered ?? 0) + (data.uncovered ?? 0),
        })
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    loadCoverage()

    return () => controller.abort()
  }, [tenantId])

  const total = coverage.total ?? coverage.covered + coverage.uncovered
  const percentage =
    total > 0 ? Math.round((coverage.covered / total) * 100) : 0

  const radius = 38
  const circumference = 2 * Math.PI * radius
  const coveredSegment =
    total > 0 ? (coverage.covered / total) * circumference : 0
  const uncoveredSegment = circumference - coveredSegment

  return (
    <Panel
      title="MITRE coverage"
      icon={<Crosshair aria-hidden="true" />}
      action={
        <Link
          href={`/dashboard/${tenantId}/mitre`}
          className="text-xs font-medium text-primary hover:underline"
        >
          View coverage
        </Link>
      }
    >
      <Link
        href={`/dashboard/${tenantId}/mitre`}
        className="group block rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        aria-label={`Open MITRE coverage. ${percentage}% of techniques covered.`}
      >
        {loading ? (
          <div className="h-32 animate-pulse rounded-md bg-muted" />
        ) : (
          <>
            <div className="flex items-center gap-5">
              <div className="relative h-32 w-32 shrink-0">
                <svg
                  viewBox="0 0 100 100"
                  className="h-full w-full -rotate-90 transition-transform group-hover:scale-105"
                  role="img"
                  aria-label={`MITRE coverage is ${percentage} percent`}
                >
                  <circle
                    cx="50"
                    cy="50"
                    r={radius}
                    fill="none"
                    stroke="var(--fill-muted, var(--muted))"
                    strokeWidth="11"
                  />

                  <circle
                    cx="50"
                    cy="50"
                    r={radius}
                    fill="none"
                    stroke="var(--fill-accent, var(--primary))"
                    strokeWidth="11"
                    strokeDasharray={`${coveredSegment} ${uncoveredSegment}`}
                    strokeDashoffset="0"
                  />
                </svg>

                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-semibold tabular text-foreground">
                    {percentage}%
                  </span>
                  <span className="text-[10px] text-muted-foreground">
                    covered
                  </span>
                </div>
              </div>

              <ul className="flex-1 space-y-3">
                <li className="flex items-center gap-2 text-xs">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{
                      backgroundColor: 'var(--fill-accent, var(--primary))',
                    }}
                    aria-hidden="true"
                  />
                  <span className="text-muted-foreground">Covered</span>
                  <span className="ml-auto font-medium tabular text-foreground">
                    {coverage.covered}
                  </span>
                </li>

                <li className="flex items-center gap-2 text-xs">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{
                      backgroundColor:
                        'var(--fill-muted, var(--muted-foreground))',
                    }}
                    aria-hidden="true"
                  />
                  <span className="text-muted-foreground">Uncovered</span>
                  <span className="ml-auto font-medium tabular text-foreground">
                    {coverage.uncovered}
                  </span>
                </li>

                <li className="border-t border-border pt-2 text-xs text-muted-foreground">
                  {coverage.covered} of {total} techniques covered
                </li>
              </ul>
            </div>

            <p className="sr-only">
              Donut chart showing {percentage}% MITRE technique coverage:
              {coverage.covered} covered and {coverage.uncovered} uncovered.
            </p>
          </>
        )}
      </Link>
    </Panel>
  )
}
