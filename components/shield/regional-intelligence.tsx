"use client"

import {
  Globe,
  Shield,
  Server,
  Activity
} from "lucide-react"

import { StatCard } from "@/components/shell/stat-card"
import { AfricaMap } from "@/components/AfricaMap"


const regions = [
  {
    country:"Nigeria",
    coverage:92,
    assets:4200
  },
  {
    country:"South Africa",
    coverage:95,
    assets:6200
  },
  {
    country:"Kenya",
    coverage:88,
    assets:1800
  },
  {
    country:"Ghana",
    coverage:81,
    assets:900
  }
]


export function RegionalIntelligence(){

return (

<div className="space-y-4">


<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">


<StatCard
label="African Assets"
value="13,100"
tone="cyber"
icon={Server}
/>


<StatCard
label="Regional Threats"
value="42"
tone="critical"
icon={Shield}
/>


<StatCard
label="Coverage"
value="91%"
tone="success"
icon={Globe}
/>


<StatCard
label="Detection Rate"
value="98%"
tone="cyber"
icon={Activity}
/>


</div>



<div className="grid lg:grid-cols-3 gap-4">


<div className="glass p-5 lg:col-span-2">

<div className="text-xs uppercase font-mono text-cyber">
Africa Threat Coverage
</div>


<div className="h-[350px] mt-4">

<AfricaMap/>

</div>


</div>




<div className="glass p-5">

<div className="text-xs uppercase font-mono text-cyber mb-4">
Regional Protection
</div>


<div className="space-y-4">


{regions.map((r)=>(

<div key={r.country}>


<div className="flex justify-between text-sm">

<span>{r.country}</span>

<span className="font-mono text-cyber">
{r.coverage}%
</span>

</div>


<div className="h-2 bg-white/10 rounded">

<div
className="h-full bg-primary rounded"
style={{
width:`${r.coverage}%`
}}
/>

</div>


<div className="text-xs text-muted-foreground mt-1">
{r.assets} assets protected
</div>


</div>

))}


</div>


</div>


</div>


</div>

)

}