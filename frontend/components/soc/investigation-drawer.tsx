'use client'

import { useState } from 'react'
import { ExternalLink, FileJson, ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { createInvestigation } from '@/lib/api/investigations'

export function InvestigationDrawer({ title = 'Investigation workspace', alertId }: { title?: string; alertId?: string }) {
  const [open, setOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [created, setCreated] = useState(false)
  const [error, setError] = useState<string | null>(null)
  async function startInvestigation() {
    if (!alertId || creating || created) return
    setCreating(true); setError(null)
    try { await createInvestigation({ title: `Investigation: ${title}`, summary: 'Investigation opened from the SOC workspace.', alert_id: alertId, status: 'open', assignee_id: null, metadata_json: {} }); setCreated(true) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Unable to create investigation.') }
    finally { setCreating(false) }
  }
  return <>
    <Button variant="outline" size="sm" onClick={() => setOpen(true)}><ShieldAlert data-icon="inline-start" /> Investigate</Button>
    <Sheet open={open} onOpenChange={setOpen}><SheetContent className="w-full overflow-y-auto sm:max-w-xl"><SheetHeader><SheetTitle>{title}</SheetTitle><SheetDescription>Evidence-first triage surface for the active tenant.</SheetDescription></SheetHeader><div className="flex flex-col gap-4 p-5">
      <div className="flex items-center justify-between rounded-md border border-border bg-muted/20 p-3"><div><p className="text-xs font-semibold text-foreground">Selected signal</p><p className="mt-1 text-xs text-muted-foreground">{alertId ? 'Alert context is attached to this workspace.' : 'Open an event or alert to populate evidence.'}</p></div><Badge variant="outline">{created ? 'Investigation open' : alertId ? 'Alert linked' : 'Awaiting context'}</Badge></div>
      <section className="rounded-md border border-border bg-card p-4"><h3 className="flex items-center gap-2 text-sm font-semibold"><FileJson className="size-4 text-primary" /> Evidence timeline</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">Correlated event context, affected entities, and analyst notes will appear here from the authenticated API.</p></section>
      <section className="rounded-md border border-border bg-card p-4"><h3 className="text-sm font-semibold">Next actions</h3><div className="mt-3 flex flex-wrap gap-2"><Button variant="secondary" size="sm" onClick={startInvestigation} disabled={!alertId || creating || created}>{creating ? 'Opening…' : created ? 'Investigation opened' : 'Start investigation'}</Button><Button variant="secondary" size="sm">Add note</Button><Button variant="ghost" size="sm"><ExternalLink data-icon="inline-start" /> Open full record</Button></div>{error && <p className="mt-3 text-sm text-destructive" role="alert">{error}</p>}</section>
    </div></SheetContent></Sheet>
  </>
}
