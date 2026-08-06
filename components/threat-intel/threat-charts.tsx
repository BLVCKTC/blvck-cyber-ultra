"use client"

import { Area, AreaChart, Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart"
import { trendData, type ThreatEvent } from "@/lib/threat-data"

const trendConfig = { critical:{label:"Critical",color:"var(--chart-4)"}, high:{label:"High",color:"var(--chart-3)"}, medium:{label:"Medium",color:"var(--chart-1)"} } satisfies ChartConfig
export function ThreatTrendChart() { return <ChartContainer config={trendConfig} className="h-64 w-full aspect-auto"><AreaChart data={trendData} margin={{left:-14,right:12}}><CartesianGrid vertical={false} strokeDasharray="3 3"/><XAxis dataKey="time" tickLine={false} axisLine={false}/><YAxis tickLine={false} axisLine={false}/><ChartTooltip content={<ChartTooltipContent indicator="line"/>}/><Area dataKey="medium" type="monotone" stackId="1" stroke="var(--color-medium)" fill="var(--color-medium)" fillOpacity={.08}/><Area dataKey="high" type="monotone" stackId="1" stroke="var(--color-high)" fill="var(--color-high)" fillOpacity={.12}/><Area dataKey="critical" type="monotone" stackId="1" stroke="var(--color-critical)" fill="var(--color-critical)" fillOpacity={.16}/></AreaChart></ChartContainer> }

const categoryConfig = { count:{label:"Signals",color:"var(--chart-1)"} } satisfies ChartConfig
export function CategoryChart({ events }: { events: ThreatEvent[] }) { const data = Object.entries(events.reduce<Record<string,number>>((a,e)=>{a[e.type]=(a[e.type]||0)+1;return a},{})).map(([type,count])=>({type,count})); return <ChartContainer config={categoryConfig} className="h-56 w-full aspect-auto"><BarChart data={data} layout="vertical" margin={{left:22}}><CartesianGrid horizontal={false}/><XAxis type="number" hide/><YAxis dataKey="type" type="category" tickLine={false} axisLine={false} width={82}/><ChartTooltip content={<ChartTooltipContent/>}/><Bar dataKey="count" fill="var(--color-count)" radius={3}/></BarChart></ChartContainer> }
