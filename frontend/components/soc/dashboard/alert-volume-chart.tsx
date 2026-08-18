'use client'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { alertVolume } from '@/lib/soc/mock'

const axisTick = { fill: 'var(--muted-foreground)', fontSize: 11 }

export function AlertVolumeChart() {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={alertVolume}
          margin={{ top: 8, right: 8, left: -16, bottom: 0 }}
        >
          <defs>
            <linearGradient id="alertsGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="escGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--critical)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="var(--critical)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--border)"
            vertical={false}
          />
          <XAxis dataKey="time" tick={axisTick} axisLine={false} tickLine={false} />
          <YAxis tick={axisTick} axisLine={false} tickLine={false} width={40} />
          <Tooltip
            contentStyle={{
              background: 'var(--popover)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              fontSize: 12,
              color: 'var(--foreground)',
            }}
            labelStyle={{ color: 'var(--muted-foreground)' }}
          />
          <Area
            type="monotone"
            dataKey="alerts"
            name="Alerts"
            stroke="var(--primary)"
            strokeWidth={2}
            fill="url(#alertsGrad)"
          />
          <Area
            type="monotone"
            dataKey="escalated"
            name="Escalated"
            stroke="var(--critical)"
            strokeWidth={2}
            fill="url(#escGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
