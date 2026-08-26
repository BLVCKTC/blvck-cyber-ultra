'use client'

import { useState } from 'react'
import { ExternalLink, FileJson, ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'

export function InvestigationDrawer({ title = 'Investigation workspace' }: { title?: string }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}><ShieldAlert data-icon="inline-start" /> Investigate</Button>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-xl">
          <SheetHeader>
            <SheetTitle>{title}</SheetTitle>
            <SheetDescription>Evidence-first triage surface for the active tenant.</SheetDescription>
          </SheetHeader>
          <div className="flex flex-col gap-4 p-5">
            <div className="flex items-center justify-between rounded-md border border-border bg-muted/20 p-3"><div><p className="text-xs font-semibold text-foreground">Selected signal</p><p className="mt-1 text-xs text-muted-foreground">Open an event or alert to populate evidence.</p></div><Badge variant="outline">Awaiting context</Badge></div>
            <section className="rounded-md border border-border bg-card p-4"><h3 className="flex items-center gap-2 text-sm font-semibold"><FileJson className="size-4 text-primary" /> Evidence timeline</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">Correlated event context, affected entities, and analyst notes will appear here from the authenticated API.</p></section>
            <section className="rounded-md border border-border bg-card p-4"><h3 className="text-sm font-semibold">Next actions</h3><div className="mt-3 flex flex-wrap gap-2"><Button variant="secondary" size="sm">Assign analyst</Button><Button variant="secondary" size="sm">Add note</Button><Button variant="ghost" size="sm"><ExternalLink data-icon="inline-start" /> Open full record</Button></div></section>
          </div>
        </SheetContent>
      </Sheet>
    </>
  )
}
