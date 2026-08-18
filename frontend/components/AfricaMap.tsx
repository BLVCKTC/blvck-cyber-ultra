"use client"

const regions = [
  {name:"South Africa",x:70,y:70},
  {name:"Zimbabwe",x:62,y:62},
  {name:"Kenya",x:75,y:40},
  {name:"Nigeria",x:45,y:38},
  {name:"Ghana",x:40,y:42},
  {name:"Egypt",x:65,y:20},
]


export function AfricaMap({
compact=false
}:{
compact?:boolean
}){


return (

<div
className={`
relative
w-full
${compact ? "h-48":"h-64"}
`}
>


<svg
viewBox="0 0 300 300"
className="h-full w-full"
>


{/* Africa outline approximation */}

<path

d="
M150 20
C110 30 80 80 70 130
C60 190 100 250 160 270
C210 230 240 170 220 100
C200 50 170 20 150 20
Z
"

fill="rgba(0,212,255,0.08)"

stroke="#00D4FF"

strokeWidth="2"

/>



{
regions.map((r)=>(


<g key={r.name}>


<circle

cx={r.x*3}

cy={r.y*3}

r="6"

fill="#00FF88"

className="animate-pulse"

/>


<text

x={r.x*3+8}

y={r.y*3}

fill="white"

fontSize="8"

>

{r.name}

</text>


</g>


))
}



</svg>


</div>

)

}