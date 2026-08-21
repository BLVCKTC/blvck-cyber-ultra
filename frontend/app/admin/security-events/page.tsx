'use client'

import { useEffect, useState } from 'react'

import {
  getSecurityEvents,
  type SecurityEvent,
} from '@/lib/api/security-events'

export default function SecurityEventsPage() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [total, setTotal] = useState(0)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadEvents() {
      try {
        setLoading(true)
        setError(null)

        const response = await getSecurityEvents({
          limit: 50,
          offset: 0,
        })

        if (cancelled) return

        setEvents(response.items)
        setTotal(response.total)
      } catch (err) {
        if (cancelled) return

        console.error('Failed to load security events:', err)

        if (err instanceof Error) {
          setError(err.message)
        } else {
          setError('Failed to load security events')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadEvents()

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <main className="p-6">
        <h1 className="text-2xl font-semibold">Security Events</h1>

        <p className="mt-4 text-sm text-muted-foreground">
          Loading security events...
        </p>
      </main>
    )
  }

  if (error) {
    return (
      <main className="p-6">
        <h1 className="text-2xl font-semibold">Security Events</h1>

        <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
          <p className="font-medium text-red-400">
            Failed to load security events
          </p>

          <p className="mt-1 text-sm text-red-300">{error}</p>
        </div>
      </main>
    )
  }

  return (
    <main className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Security Events</h1>

        <p className="mt-1 text-sm text-muted-foreground">
          Live security telemetry from the BLVCK CYBER backend.
        </p>
      </div>

      <div className="rounded-lg border p-4">
        <div className="text-sm text-muted-foreground">Total Events</div>

        <div className="mt-1 text-3xl font-semibold">{total}</div>
      </div>

      <div className="overflow-hidden rounded-lg border">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b bg-muted/30">
              <tr>
                <th className="px-4 py-3 text-left">Time</th>

                <th className="px-4 py-3 text-left">Severity</th>

                <th className="px-4 py-3 text-left">Event</th>

                <th className="px-4 py-3 text-left">Source</th>

                <th className="px-4 py-3 text-left">Host</th>

                <th className="px-4 py-3 text-left">Source IP</th>

                <th className="px-4 py-3 text-left">User</th>
              </tr>
            </thead>

            <tbody>
              {events.map((event) => (
                <tr key={event.id} className="border-b last:border-0">
                  <td className="px-4 py-3 whitespace-nowrap">
                    {new Date(event.timestamp).toLocaleString()}
                  </td>

                  <td className="px-4 py-3">
                    <span
                      className={[
                        'rounded-full px-2 py-1 text-xs font-medium',
                        event.severity === 'critical'
                          ? 'bg-red-500/20 text-red-400'
                          : event.severity === 'high'
                            ? 'bg-orange-500/20 text-orange-400'
                            : event.severity === 'medium'
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-green-500/20 text-green-400',
                      ].join(' ')}
                    >
                      {event.severity.toUpperCase()}
                    </span>
                  </td>

                  <td className="px-4 py-3 font-medium">{event.event_type}</td>

                  <td className="px-4 py-3">{event.source}</td>

                  <td className="px-4 py-3">{event.hostname ?? '—'}</td>

                  <td className="px-4 py-3 font-mono">
                    {event.source_ip ?? '—'}
                  </td>

                  <td className="px-4 py-3">{event.user_identifier ?? '—'}</td>
                </tr>
              ))}

              {events.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-12 text-center text-muted-foreground"
                  >
                    No security events found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  )
}
