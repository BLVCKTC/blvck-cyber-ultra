'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  ChevronLeft,
  ChevronRight,
  Clock3,
  ExternalLink,
  FileJson,
  Filter,
  RefreshCw,
  Search,
  ShieldCheck,
  X,
} from 'lucide-react'
import { toast } from 'sonner'

import {
  getSecurityEvents,
  updateSecurityEvent,
  type SecurityEvent,
  type SecurityEventSeverity,
  type SecurityEventStatus,
} from '@/lib/api/security-events'
import { SeverityBadge } from '@/components/soc/severity'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Skeleton } from '@/components/ui/skeleton'

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 250
type SeverityFilter = 'all' | SecurityEventSeverity
type StatusFilter = 'all' | SecurityEventStatus

const dateFormatter = new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium', timeStyle: 'medium' })
const shortFormatter = new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium', timeStyle: 'short' })

function formatTimestamp(value?: string | null, short = false) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : (short ? shortFormatter : dateFormatter).format(date)
}
function display(value?: string | number | null) { return value === null || value === undefined || value === '' ? '—' : String(value) }
function riskTone(score?: number | null) { return score == null ? 'text-muted-foreground' : score >= 80 ? 'text-critical' : score >= 50 ? 'text-warning' : 'text-success' }

function JsonBlock({ label, value }: { label: string; value?: Record<string, unknown> | null }) {
  return (
    <details className="group rounded-md border border-border/70 bg-muted/20">
      <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2 text-xs font-medium text-foreground [&::-webkit-details-marker]:hidden">
        <FileJson className="size-3.5 text-muted-foreground" /> {label}
        <span className="ml-auto text-muted-foreground group-open:rotate-90">›</span>
      </summary>
      <pre className="max-h-56 overflow-auto border-t border-border/60 p-3 font-mono text-[10px] leading-relaxed text-muted-foreground">{value ? JSON.stringify(value, null, 2) : 'No data available'}</pre>
    </details>
  )
}

function EventDetail({ event, onProcess, processing }: { event: SecurityEvent; onProcess: () => void; processing: boolean }) {
  return (
    <div className="flex flex-col gap-5 overflow-y-auto px-5 pb-6">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2"><SeverityBadge severity={event.severity} /><span className="rounded border border-border px-2 py-0.5 font-mono text-[10px] uppercase text-muted-foreground">{event.status}</span></div>
        <span className={`font-mono text-lg font-semibold ${riskTone(event.risk_score)}`}>{display(event.risk_score)}<span className="text-[10px] font-normal text-muted-foreground"> / risk</span></span>
      </div>
      <div><p className="font-mono text-xs text-primary">{event.event_type}</p><h3 className="mt-1 text-lg font-semibold text-foreground text-pretty">{display(event.message)}</h3><p className="mt-2 break-all font-mono text-[10px] text-muted-foreground">{event.id}</p></div>
      <section className="flex flex-col gap-3"><h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Event timeline</h4><div className="grid grid-cols-1 gap-2 text-xs sm:grid-cols-3">{[['Event time', event.event_time], ['Ingested', event.ingested_at], ['Created', event.created_at]].map(([label, value]) => <div key={label} className="rounded-md border border-border/70 bg-muted/20 p-3"><p className="text-muted-foreground">{label}</p><p className="mt-1 font-mono text-[10px] text-foreground">{formatTimestamp(value)}</p></div>)}</div></section>
      <section className="grid grid-cols-2 gap-x-4 gap-y-3 border-y border-border/70 py-4 text-xs"><h4 className="col-span-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Forensic context</h4>{[['Source', event.source], ['Source type', event.source_type], ['Category', event.event_category], ['Host', event.hostname], ['Source IP', event.source_ip], ['Destination IP', event.destination_ip], ['Protocol', event.protocol], ['User', event.user_identifier], ['MITRE tactic', event.mitre_tactic], ['MITRE technique', event.mitre_technique_id || event.mitre_technique], ['Process', event.process_name], ['Action', event.action]].map(([label, value]) => <div key={label}><dt className="text-muted-foreground">{label}</dt><dd className="mt-1 break-all font-mono text-[11px] text-foreground">{display(value)}</dd></div>)}</section>
      <div className="flex flex-col gap-2"><JsonBlock label="Normalized data" value={event.normalized_data} /><JsonBlock label="Raw event" value={event.raw_event} /><JsonBlock label="Event metadata" value={event.event_metadata} /></div>
      {event.status !== 'processed' && <Button onClick={onProcess} disabled={processing} className="w-full"><ShieldCheck data-icon="inline-start" />{processing ? 'Processing event…' : 'Mark as processed'}</Button>}
    </div>
  )
}

export function SecurityEventsTable({ tenantId }: { tenantId: string }) {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [totalAvailable, setTotalAvailable] = useState(0)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [query, setQuery] = useState('')
  const [severity, setSeverity] = useState<SeverityFilter>('all')
  const [status, setStatus] = useState<StatusFilter>('all')
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState<SecurityEvent | null>(null)
  const [processingId, setProcessingId] = useState<string | null>(null)
  const sequence = useRef(0)
  const trimmedQuery = query.trim()
  const totalPages = Math.max(1, Math.ceil(totalAvailable / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)

  const fetchEvents = useCallback(async (isRefresh = false) => {
    const requestId = ++sequence.current
    isRefresh ? setRefreshing(true) : setLoading(true)
    try {
      const response = await getSecurityEvents({ tenantId, q: trimmedQuery || undefined, severity: severity === 'all' ? undefined : severity, status: status === 'all' ? undefined : status, limit: PAGE_SIZE, offset: (currentPage - 1) * PAGE_SIZE })
      if (requestId === sequence.current) { setEvents(response.items); setTotalAvailable(response.total) }
    } catch (error) { if (requestId === sequence.current) { console.error('Failed to load security events:', error); toast.error('Failed to load security events') } }
    finally { if (requestId === sequence.current) { setLoading(false); setRefreshing(false) } }
  }, [currentPage, severity, status, tenantId, trimmedQuery])

  useEffect(() => { if (page !== 1 && (trimmedQuery || severity !== 'all' || status !== 'all')) { setPage(1); return }; const id = window.setTimeout(() => void fetchEvents(), SEARCH_DEBOUNCE_MS); return () => window.clearTimeout(id) }, [fetchEvents, page, severity, status, trimmedQuery])
  useEffect(() => { if (page > totalPages) setPage(totalPages) }, [page, totalPages])

  const counts = useMemo(() => events.reduce((acc, event) => { acc[event.severity] += 1; return acc }, { critical: 0, high: 0, medium: 0, low: 0 }), [events])
  const processing = selected?.id === processingId
  const handleProcess = async (event: SecurityEvent) => {
    if (event.status === 'processed' || processingId) return
    setProcessingId(event.id)
    try { const updated = await updateSecurityEvent(event.id, { status: 'processed' }); setEvents((items) => items.map((item) => item.id === event.id ? updated : item)); setSelected(updated); toast.success('Event marked as processed') }
    catch (error) { console.error('Failed to update security event:', error); toast.error('Failed to update event status') }
    finally { setProcessingId(null) }
  }
  const reset = () => { setQuery(''); setSeverity('all'); setStatus('all'); setPage(1) }
  const rangeStart = totalAvailable === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(currentPage * PAGE_SIZE, totalAvailable)

  return <div className="flex flex-col gap-4">
    <div className="flex flex-col gap-3 rounded-md border border-border/70 bg-muted/10 p-3 xl:flex-row xl:items-center">
      <div className="relative min-w-0 flex-1"><Search aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" /><Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search event, host, IP, user, or source…" className="pl-9" aria-label="Search security events" /></div>
      <div className="flex flex-wrap items-center gap-2"><Filter aria-hidden="true" className="size-4 text-muted-foreground" /><select value={severity} onChange={(e) => { setSeverity(e.target.value as SeverityFilter); setPage(1) }} className="h-9 rounded-md border border-input bg-background px-2 text-xs" aria-label="Filter by severity"><option value="all">All severities</option><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select><select value={status} onChange={(e) => { setStatus(e.target.value as StatusFilter); setPage(1) }} className="h-9 rounded-md border border-input bg-background px-2 text-xs" aria-label="Filter by status"><option value="all">All statuses</option><option value="open">Open</option><option value="processing">Processing</option><option value="processed">Processed</option><option value="failed">Failed</option><option value="suppressed">Suppressed</option></select><Button type="button" variant="outline" size="sm" onClick={reset} disabled={!trimmedQuery && severity === 'all' && status === 'all'}><X data-icon="inline-start" />Reset</Button><Button type="button" variant="outline" size="icon" onClick={() => void fetchEvents(true)} disabled={loading || refreshing} aria-label="Refresh security events"><RefreshCw className={refreshing ? 'animate-spin' : ''} /></Button></div>
    </div>
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted-foreground"><span className="font-mono">RESULT SET: {totalAvailable}</span><span className="text-critical">{counts.critical} critical</span><span className="text-high">{counts.high} high</span><span className="text-warning">{counts.medium} medium</span><span className="text-info">{counts.low} low</span></div>
    <div className="overflow-x-auto rounded-md border" aria-busy={loading || refreshing}><table className="w-full min-w-[980px] text-left text-sm"><caption className="sr-only">Security event stream</caption><thead className="border-b bg-muted/30 text-[10px] uppercase tracking-wider text-muted-foreground"><tr>{['Severity', 'Event / MITRE', 'Source', 'Host / Network', 'Identity', 'Risk', 'Observed', 'Status', ''].map((heading) => <th key={heading} scope="col" className="whitespace-nowrap px-3 py-3 font-medium">{heading}</th>)}</tr></thead><tbody>{loading ? Array.from({ length: 6 }, (_, index) => <tr key={index} className="border-b"><td className="px-3 py-4" colSpan={9}><Skeleton className="h-5 w-full" /></td></tr>) : events.length === 0 ? <tr><td colSpan={9} className="px-4 py-14 text-center text-sm text-muted-foreground"><Clock3 className="mx-auto mb-2 size-5" />No security events match the current filters.</td></tr> : events.map((event) => <tr key={event.id} onClick={() => setSelected(event)} className={`cursor-pointer border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40 ${selected?.id === event.id ? 'bg-primary/5' : ''}`}><td className="px-3 py-3"><SeverityBadge severity={event.severity} /></td><td className="max-w-[250px] px-3 py-3"><div className="font-medium text-foreground">{event.event_type}</div><div className="truncate text-xs text-muted-foreground" title={event.message ?? undefined}>{display(event.message)}</div>{event.mitre_technique_id && <div className="mt-1 font-mono text-[10px] text-primary">{event.mitre_technique_id} · {display(event.mitre_technique)}</div>}</td><td className="px-3 py-3"><div className="font-medium">{event.source}</div><div className="text-[10px] text-muted-foreground">{event.source_type}</div></td><td className="px-3 py-3 font-mono text-[11px]"><div>{display(event.hostname)}</div><div className="text-muted-foreground">{display(event.source_ip)}{event.destination_ip ? ` → ${event.destination_ip}` : ''}</div></td><td className="max-w-[130px] truncate px-3 py-3 text-xs">{display(event.user_identifier)}</td><td className={`px-3 py-3 font-mono font-semibold ${riskTone(event.risk_score)}`}>{display(event.risk_score)}</td><td className="whitespace-nowrap px-3 py-3 text-[10px] text-muted-foreground"><span title={formatTimestamp(event.event_time)}>{formatTimestamp(event.event_time, true)}</span></td><td className="px-3 py-3"><span className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px] uppercase text-muted-foreground">{event.status}</span></td><td className="px-3 py-3"><ExternalLink className="size-3.5 text-muted-foreground" /></td></tr>)}</tbody></table></div>
    <div className="flex items-center justify-between text-xs text-muted-foreground" aria-live="polite"><span>Showing {rangeStart}–{rangeEnd} of {totalAvailable}</span><div className="flex items-center gap-1"><Button type="button" size="icon-sm" variant="outline" disabled={currentPage <= 1 || loading} onClick={() => setPage((p) => p - 1)} aria-label="Previous page"><ChevronLeft /></Button><span className="px-2 font-mono">{currentPage} / {totalPages}</span><Button type="button" size="icon-sm" variant="outline" disabled={currentPage >= totalPages || loading} onClick={() => setPage((p) => p + 1)} aria-label="Next page"><ChevronRight /></Button></div></div>
    <Sheet open={Boolean(selected)} onOpenChange={(open) => !open && setSelected(null)}><SheetContent side="right" className="w-full gap-0 overflow-hidden p-0 sm:max-w-xl"><SheetHeader className="border-b border-border/70 pr-14"><SheetTitle>Event investigation</SheetTitle><SheetDescription>Forensic detail for the selected telemetry record.</SheetDescription></SheetHeader>{selected && <EventDetail event={selected} onProcess={() => void handleProcess(selected)} processing={Boolean(processing)} />}</SheetContent></Sheet>
  </div>
}

export { formatTimestamp }
