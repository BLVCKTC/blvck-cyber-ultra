'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Command, Search, ShieldAlert, Activity, Crosshair, Server, BriefcaseBusiness, X } from 'lucide-react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

const categories = [
  { label: 'Events', icon: Activity, href: '/security/events' },
  { label: 'Alerts', icon: ShieldAlert, href: '/security/alerts' },
  { label: 'Detection rules', icon: Crosshair, href: '/detection/rules' },
  { label: 'Investigations', icon: BriefcaseBusiness, href: '/dashboard/demo/investigations' },
  { label: 'Hosts', icon: Server, href: '/dashboard/demo/assets' },
]

export function GlobalSearch() {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')

  function openCategory(href: string) {
    setOpen(false)
    setQuery('')
    router.push(href)
  }

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setOpen(true)
      }
      if (event.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className="hidden h-9 min-w-64 items-center gap-2 rounded-md border border-border bg-card px-3 text-left text-sm text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground md:flex" aria-label="Open global search">
        <Search className="size-4" />
        <span className="flex-1">Search your environment</span>
        <kbd className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px]">⌘K</kbd>
      </button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="gap-0 overflow-hidden p-0 sm:max-w-xl">
          <DialogHeader className="border-b border-border px-4 py-3">
            <DialogTitle className="flex items-center gap-2 text-sm"><Command className="size-4 text-primary" /> Global investigation search</DialogTitle>
            <DialogDescription className="sr-only">Search events, alerts, rules, and entities in the active tenant.</DialogDescription>
          </DialogHeader>
          <div className="flex items-center gap-2 border-b border-border px-4 py-3"><Search className="size-4 text-muted-foreground" /><Input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search events, alerts, hosts, rules…" className="border-0 p-0 shadow-none focus-visible:ring-0" /><button type="button" onClick={() => setQuery('')} aria-label="Clear search"><X className="size-4 text-muted-foreground" /></button></div>
          <div className="flex flex-col gap-2 p-3">
            <p className="px-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Search categories</p>
            {categories.map(({ label, icon: Icon, href }) => <button key={label} type="button" onClick={() => openCategory(href)} className="flex items-center gap-3 rounded-md px-3 py-2.5 text-left text-sm hover:bg-accent"><Icon className="size-4 text-muted-foreground" /><span className="flex-1">{label}</span><Badge variant="outline">{query ? 'Search' : 'Browse'}</Badge></button>)}
            <p className="px-2 pt-2 text-xs text-muted-foreground">Results are scoped to the authenticated tenant and backend permissions.</p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export function SearchTrigger() { return <GlobalSearch /> }

export default GlobalSearch

// Keep the compiler from treating the imported search icon as unused in future variants.
void Search
