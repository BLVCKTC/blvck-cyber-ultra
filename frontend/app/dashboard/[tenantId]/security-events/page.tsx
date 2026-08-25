import { SectionHeading } from '@/components/soc/shell'
import { Panel } from '@/components/soc/panel'
import { SecurityEventsTable } from '@/components/soc/security-events/security-events-table'
import { Activity, AlertTriangle, Clock3, Radio, ShieldAlert } from 'lucide-react'

export const metadata = { title: 'Security Events — BLVCK CYBER' }

export default async function SecurityEventsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params

  return (
    <div className="flex flex-col gap-6">
      <SectionHeading
        title="Security Events"
        sub="Investigate normalized telemetry across your organization’s security estate."
        action={<div className="flex items-center gap-2 rounded-md border border-success/25 bg-success/10 px-3 py-1.5"><span className="size-1.5 rounded-full bg-success" /><span className="font-mono text-[10px] font-medium uppercase tracking-wider text-success">Live telemetry</span></div>}
      />

      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        <Panel title="Result set" icon={<Activity className="size-4" />} bodyClassName="pt-3"><div className="font-mono text-2xl font-semibold text-foreground">—</div><p className="mt-1 text-xs text-muted-foreground">Current filtered records</p></Panel>
        <Panel title="Critical" icon={<ShieldAlert className="size-4" />} bodyClassName="pt-3"><div className="font-mono text-2xl font-semibold text-critical">—</div><p className="mt-1 text-xs text-muted-foreground">Immediate investigation</p></Panel>
        <Panel title="High risk" icon={<AlertTriangle className="size-4" />} bodyClassName="pt-3"><div className="font-mono text-2xl font-semibold text-warning">—</div><p className="mt-1 text-xs text-muted-foreground">Priority analyst queue</p></Panel>
        <Panel title="Collection" icon={<Radio className="size-4" />} bodyClassName="pt-3"><div className="font-mono text-2xl font-semibold text-success">ACTIVE</div><p className="mt-1 text-xs text-muted-foreground">Streaming from sources</p></Panel>
      </div>

      <Panel title="Event stream" icon={<Clock3 className="size-4" />} action={<span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Analyst workspace</span>} bodyClassName="p-3 sm:p-4">
        <SecurityEventsTable tenantId={tenantId} />
      </Panel>
    </div>
  )
}
