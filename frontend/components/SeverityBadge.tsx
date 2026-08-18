"use client"

type Severity =
  | "Critical"
  | "High"
  | "Medium"
  | "Low"
  | "Informational"


interface SeverityBadgeProps {

  severity: Severity | string

}



export function SeverityBadge({
  severity,
}: SeverityBadgeProps) {


const styles:Record<string,string> = {


Critical:
"bg-red-500/20 text-red-400 border-red-500/30",


High:
"bg-orange-500/20 text-orange-400 border-orange-500/30",


Medium:
"bg-yellow-500/20 text-yellow-400 border-yellow-500/30",


Low:
"bg-green-500/20 text-green-400 border-green-500/30",


Informational:
"bg-blue-500/20 text-blue-400 border-blue-500/30",

}



return (

<span

className={`
inline-flex
items-center
rounded-md
border
px-2
py-1
text-[10px]
font-mono
uppercase
tracking-widest

${styles[severity] ?? styles.Informational}

`}

>

{severity}

</span>

)

}