'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight, RefreshCw, Search } from 'lucide-react'
import { toast } from 'sonner'

import {
  getSecurityEvents,
  updateSecurityEvent,
  type SecurityEvent,
  type SecurityEventSeverity,
} from '@/lib/api/security-events'
import { SeverityBadge } from '@/components/soc/severity'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

type Props = {
  tenantId: string
}

type SeverityFilter = 'all' | SecurityEventSeverity

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 250

const timestampFormatter = new Intl.DateTimeFormat('en-GB', {
  dateStyle: 'medium',
  timeStyle: 'medium',
})

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)

  return Number.isNaN(date.getTime())
    ? timestamp
    : timestampFormatter.format(date)
}

export function SecurityEventsTable({ tenantId }: Props) {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [totalAvailable, setTotalAvailable] = useState(0)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [query, setQuery] = useState('')
  const [severity, setSeverity] = useState<SeverityFilter>('all')
  const [page, setPage] = useState(1)
  const [processingEventIds, setProcessingEventIds] = useState<Set<string>>(
    () => new Set(),
  )

  const requestSequence = useRef(0)
  const processingIds = useRef(new Set<string>())

  const totalPages = Math.max(1, Math.ceil(totalAvailable / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const trimmedQuery = query.trim()

  const fetchEvents = useCallback(
    async (isRefresh = false) => {
      const requestId = ++requestSequence.current

      if (isRefresh) {
        setRefreshing(true)
        setLoading(false)
      } else {
        setLoading(true)
        setRefreshing(false)
      }

      try {
        const response = await getSecurityEvents({
          tenantId,
          q: trimmedQuery || undefined,
          severity: severity === 'all' ? undefined : severity,
          limit: PAGE_SIZE,
          offset: (currentPage - 1) * PAGE_SIZE,
        })

        if (requestId !== requestSequence.current) {
          return
        }

        setEvents(response.items)
        setTotalAvailable(response.total)
      } catch (error) {
        if (requestId !== requestSequence.current) {
          return
        }

        console.error('Failed to load security events:', error)
        toast.error('Failed to load security events')
      } finally {
        if (requestId === requestSequence.current) {
          setLoading(false)
          setRefreshing(false)
        }
      }
    },
    [currentPage, severity, tenantId, trimmedQuery],
  )

  useEffect(() => {
    if (page !== 1 && (trimmedQuery || severity !== 'all')) {
      setPage(1)
      return
    }

    const timeoutId = window.setTimeout(() => {
      void fetchEvents()
    }, SEARCH_DEBOUNCE_MS)

    return () => window.clearTimeout(timeoutId)
  }, [fetchEvents, page, severity, trimmedQuery])

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages)
    }
  }, [page, totalPages])

  const handleReset = () => {
    setQuery('')
    setSeverity('all')
    setPage(1)
  }

  const handleProcess = async (event: SecurityEvent) => {
    if (event.status === 'processed' || processingIds.current.has(event.id)) {
      return
    }

    processingIds.current.add(event.id)

    setProcessingEventIds((current) => {
      const next = new Set(current)
      next.add(event.id)
      return next
    })

    try {
      await updateSecurityEvent(event.id, {
        status: 'processed',
      })

      setEvents((current) =>
        current.map((item) =>
          item.id === event.id ? { ...item, status: 'processed' } : item,
        ),
      )

      toast.success('Event marked as processed')
    } catch (error) {
      console.error('Failed to update security event:', error)
      toast.error('Failed to update event status')
    } finally {
      processingIds.current.delete(event.id)

      setProcessingEventIds((current) => {
        const next = new Set(current)
        next.delete(event.id)
        return next
      })
    }
  }

  const rangeStart =
    totalAvailable === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(currentPage * PAGE_SIZE, totalAvailable)

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1">
          <Search
            aria-hidden="true"
            className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          />

          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search event, host, IP, user, or source..."
            className="pl-9"
            aria-label="Search security events"
          />
        </div>

        <select
          value={severity}
          onChange={(event) => {
            setSeverity(event.target.value as SeverityFilter)
            setPage(1)
          }}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          aria-label="Filter by severity"
        >
          <option value="all">All severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleReset}
            disabled={!trimmedQuery && severity === 'all'}
          >
            Reset
          </Button>

          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={() => void fetchEvents(true)}
            disabled={loading || refreshing}
            aria-label="Refresh security events"
            title="Refresh security events"
          >
            <RefreshCw
              aria-hidden="true"
              className={refreshing ? 'h-4 w-4 animate-spin' : 'h-4 w-4'}
            />
          </Button>
        </div>
      </div>

      <div
        className="overflow-x-auto rounded-lg border"
        aria-busy={loading || refreshing}
      >
        <table className="w-full text-sm">
          <caption className="sr-only">Security events</caption>

          <thead className="border-b bg-muted/30">
            <tr>
              {[
                'Severity',
                'Event',
                'Source',
                'Host',
                'Network',
                'User',
                'Timestamp',
              ].map((heading) => (
                <th
                  key={heading}
                  scope="col"
                  className="px-4 py-3 text-left font-medium"
                >
                  {heading}
                </th>
              ))}

              <th scope="col" className="px-4 py-3 text-right font-medium">
                Actions
              </th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td
                  colSpan={8}
                  className="px-4 py-12 text-center text-muted-foreground"
                >
                  Loading telemetry...
                </td>
              </tr>
            ) : events.length === 0 ? (
              <tr>
                <td
                  colSpan={8}
                  className="px-4 py-12 text-center text-muted-foreground"
                >
                  No security events match the current filters.
                </td>
              </tr>
            ) : (
              events.map((event) => {
                const isProcessing = processingEventIds.has(event.id)
                const isProcessed = event.status === 'processed'

                return (
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
                        <div
                          className="mt-1 max-w-xs truncate text-xs text-muted-foreground"
                          title={event.message}
                        >
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

                    <td className="px-4 py-3">
                      {event.user_identifier ?? '—'}
                    </td>

                    <td className="whitespace-nowrap px-4 py-3 text-xs text-muted-foreground">
                      {formatTimestamp(event.event_time)}
                    </td>

                    <td className="px-4 py-3 text-right">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-8 text-xs"
                        disabled={isProcessing || isProcessed}
                        onClick={() => void handleProcess(event)}
                      >
                        {isProcessing
                          ? 'Processing...'
                          : isProcessed
                            ? 'Processed'
                            : 'Mark processed'}
                      </Button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <div
        className="flex items-center justify-between text-xs text-muted-foreground"
        aria-live="polite"
      >
        <span>
          Showing {rangeStart}–{rangeEnd} of {totalAvailable}
        </span>

        <div className="flex items-center gap-1">
          <Button
            type="button"
            size="icon-sm"
            variant="outline"
            disabled={currentPage <= 1 || loading}
            onClick={() => setPage((current) => current - 1)}
            aria-label="Previous page"
          >
            <ChevronLeft aria-hidden="true" />
          </Button>

          <span className="px-2">
            Page {currentPage} of {totalPages}
          </span>

          <Button
            type="button"
            size="icon-sm"
            variant="outline"
            disabled={currentPage >= totalPages || loading}
            onClick={() => setPage((current) => current + 1)}
            aria-label="Next page"
          >
            <ChevronRight aria-hidden="true" />
          </Button>
        </div>
      </div>
    </div>
  )
}
