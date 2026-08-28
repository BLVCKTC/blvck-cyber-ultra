'use client'

import { useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { alertVolume } from '@/lib/soc/mock'

const ranges = ['Hourly', 'Daily', 'Weekly', 'Monthly', 'Yearly'] as const
const rangeData = {
  Hourly: alertVolume,
  Daily: alertVolume.map((item, index) => ({ ...item, time: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index] ?? item.time, alerts: item.alerts * 2, escalated: item.escalated * 2 })),
  Weekly: alertVolume.slice(0, 4).map((item, index) => ({ ...item, time: `W${index + 1}`, alerts: item.alerts * 7, escalated: item.escalated * 7 })),
  Monthly: alertVolume.slice(0, 6).map((item, index) => ({ ...item, time: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][index], alerts: item.alerts * 28, escalated: item.escalated * 28 })),
  Yearly: alertVolume.slice(0, 5).map((item, index) => ({ ...item, time: `${2022 + index}`, alerts: item.alerts * 365, escalated: item.escalated * 365 })),
}

const axisTick = { fill: 'var(--muted-foreground)', fontSize: 11 }

export function AlertVolumeChart() {
  const [range, setRange] = useState<(typeof ranges)[number]>('Daily')
  const data = rangeData[range]
  const max = Math.max(...data.map((item) => item.alerts))

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5"><span className="size-2 rounded-sm bg-primary" /> Alerts</span>
          <span className="flex items-center gap-1.5"><span className="size-2 rounded-sm bg-critical" /> Escalated</span>
        </div>
        <div className="flex gap-1" role="tablist" aria-label="Alert volume range">
          {ranges.map((item) => (
            <button key={item} type="button" role="tab" aria-selected={range === item} onClick={() => setRange(item)} className={`rounded-md border px-2.5 py-1 text-xs transition-colors ${range === item ? 'border-primary bg-primary/10 text-primary' : 'border-border text-muted-foreground hover:text-foreground'}`}>
              {item}
            </button>
          ))}
        </div>
      </div>
      <p className="sr-only">Stacked bar chart showing total alert volume and escalated alerts for the selected {range.toLowerCase()} range.</p>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="time" tick={axisTick} axisLine={false} tickLine={false} />
            <YAxis domain={[0, max]} tick={axisTick} axisLine={false} tickLine={false} width={40} />
            <Tooltip cursor={{ fill: 'var(--muted)', opacity: 0.35 }} contentStyle={{ background: 'var(--popover)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, color: 'var(--foreground)' }} />
            <Bar dataKey="alerts" name="Base alerts" stackId="volume" fill="var(--primary)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="escalated" name="Escalated" stackId="volume" fill="var(--critical)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
