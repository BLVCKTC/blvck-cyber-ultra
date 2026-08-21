'use client'

import { useEffect, useState, useCallback } from 'react'
import { Search, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import type {
  SecurityEvent,
  SecurityEventSeverity,
} from '@/lib/api/security-events'
import {
  getSecurityEvents,
  updateSecurityEvent,
} from '@/lib/api/security-events'

import { SeverityBadge } from '@/components/soc/severity'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

type Props = {
  tenantId: string
}

const PAGE_SIZE = 20

function formatTimestamp(timestamp: string) {
  const dt = new Date(timestamp)
  if (Number.isNaN(dt.getTime())) return timestamp

  return new Intl.DateTimeFormat('en-GB', {
    dateStyle: 'medium',
    timeStyle: 'medium',
  }).format(dt)
}

export function SecurityEventsTable({ tenantId }: Props) {
  // Data State
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [totalAvailable, setTotalAvailable] = useState(0)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  // Filter State
  const [query, setQuery] = useState('')
  const [severity, setSeverity] = useState<'all' | SecurityEventSeverity>('all')
  const [page, setPage] = useState(1)

  const fetchEvents = useCallback(
    async (isRefresh = false) => {
      try {
        isRefresh ? setRefreshing(true) : setLoading(true)

        // Passed token as the first argument
        const response = await getSecurityEvents({
          q: query.trim() || undefined,
          severity: severity === 'all' ? undefined : severity,
          limit: PAGE_SIZE,
          offset: (page - 1) * PAGE_SIZE,
        })

        setEvents(response.items)
        setTotalAvailable(response.total)
      } catch (error) {
        toast.error('Failed to load security events')
        console.error(error)
      } finally {
        setLoading(false)
        setRefreshing(false)
      }
    },
    [page, query, severity],
  )

  useEffect(() => {
    void fetchEvents()
  }, [fetchEvents])

  useEffect(() => {
    setPage(1)
  }, [query, severity])

  const handleTriage = async (eventId: string) => {
    try {
      await updateSecurityEvent(eventId, { status: 'resolved' })
      toast.success('Event marked as resolved')
      void fetchEvents(true)
    } catch (error) {
      toast.error('Failed to update event status')
    }
  }

  const totalPages = Math.max(1, Math.ceil(totalAvailable / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search event, host, IP, user, or source..."
            className="pl-9"
          />
        </div>

        <select
          value={severity}
          onChange={(e) =>
            setSeverity(e.target.value as 'all' | SecurityEventSeverity)
          }
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="all">All severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => {
              setQuery('')
              setSeverity('all')
              setPage(1)
            }}
          >
            Reset
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => void fetchEvents(true)}
            disabled={refreshing}
          >
            <RefreshCw
              className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`}
            />
          </Button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="border-b bg-muted/30">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Severity</th>
              <th className="px-4 py-3 text-left font-medium">Event</th>
              <th className="px-4 py-3 text-left font-medium">Source</th>
              <th className="px-4 py-3 text-left font-medium">Host</th>
              <th className="px-4 py-3 text-left font-medium">Network</th>
              <th className="px-4 py-3 text-left font-medium">User</th>
              <th className="px-4 py-3 text-left font-medium">Timestamp</th>
              <th className="px-4 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td
                  colSpan={8}
                  className="px-4 py-12 text-center text-sm text-muted-foreground"
                >
                  Loading telemetry...
                </td>
              </tr>
            ) : events.length === 0 ? (
              <tr>
                <td
                  colSpan={8}
                  className="px-4 py-12 text-center text-sm text-muted-foreground"
                >
                  No security events match the current filters.
                </td>
              </tr>
            ) : (
              events.map((event) => (
                <tr
                  key={event.id}
                  className="border-b transition-colors hover:bg-muted/20"
                >
                  <td className="px-4 py-3">
                    <SeverityBadge severity={event.severity} />
                  </td>

                  <td className="px-4 py-3">
                    <div className="font-medium">{event.event_type}</div>
                    {event.message && (
                      <div className="mt-1 max-w-xs truncate text-xs text-muted-foreground">
                        {event.message}
                      </div>
                    )}
                    <div className="mt-1 font-mono text-[10px] text-muted-foreground">
                      {event.id}
                    </div>
                  </td>

                  <td className="px-4 py-3">
                    <div className="font-medium">{event.source}</div>
                    <div className="text-xs text-muted-foreground">
                      {event.source_type}
                    </div>
                  </td>

                  <td className="px-4 py-3 font-mono text-xs">
                    {event.hostname ?? '—'}
                  </td>

                  <td className="px-4 py-3 font-mono text-xs">
                    <div>{event.source_ip ?? '—'}</div>
                    {event.destination_ip && (
                      <div className="text-muted-foreground">
                        → {event.destination_ip}
                      </div>
                    )}
                  </td>

                  <td className="px-4 py-3">{event.user_identifier ?? '—'}</td>

                  <td className="whitespace-nowrap px-4 py-3 text-xs text-muted-foreground">
                    {formatTimestamp(event.timestamp)}
                  </td>

                  <td className="px-4 py-3 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleTriage(event.id)}
                      className="h-8 text-xs"
                    >
                      Resolve
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>
          Showing {totalAvailable === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1}
          {' – '}
          {Math.min(currentPage * PAGE_SIZE, totalAvailable)} of{' '}
          {totalAvailable}
        </span>

        <div className="flex items-center gap-1">
          <Button
            size="icon-sm"
            variant="outline"
            disabled={currentPage <= 1}
            onClick={() => setPage(currentPage - 1)}
            aria-label="Previous page"
          >
            <ChevronLeft />
          </Button>

          <span className="px-2">
            {currentPage} / {totalPages}
          </span>

          <Button
            size="icon-sm"
            variant="outline"
            disabled={currentPage >= totalPages}
            onClick={() => setPage(currentPage + 1)}
            aria-label="Next page"
          >
            <ChevronRight />
          </Button>
        </div>
      </div>
    </div>
  )
}
