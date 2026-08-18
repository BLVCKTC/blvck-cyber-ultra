import type { LucideIcon } from "lucide-react"
import { ArrowDownRight, ArrowUpRight } from "lucide-react"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import { cn } from "@/lib/utils"


type StatTone =
  | "default"
  | "critical"
  | "success"
  | "warning"
  | "cyber"


interface StatCardProps {
  label: string
  value: string | number
  change?: string
  trend?: "up" | "down"
  icon: LucideIcon
  detail?: string
  tone?: StatTone
}


const toneStyles: Record<
  StatTone,
  {
    border: string
    icon: string
    trendUp: string
    trendDown: string
  }
> = {

  default: {
    border: "bg-primary/60",
    icon: "text-primary",
    trendUp: "text-primary",
    trendDown: "text-destructive",
  },


  cyber: {
    border: "bg-cyber",
    icon: "text-cyber",
    trendUp: "text-cyber",
    trendDown: "text-destructive",
  },


  critical: {
    border: "bg-critical",
    icon: "text-critical",
    trendUp: "text-critical",
    trendDown: "text-critical",
  },


  success: {
    border: "bg-success",
    icon: "text-success",
    trendUp: "text-success",
    trendDown: "text-warning",
  },


  warning: {
    border: "bg-warning",
    icon: "text-warning",
    trendUp: "text-warning",
    trendDown: "text-critical",
  },

}



export function StatCard({
  label,
  value,
  change,
  trend = "up",
  icon: Icon,
  detail,
  tone = "default",
}: StatCardProps) {


  const Trend =
    trend === "up"
      ? ArrowUpRight
      : ArrowDownRight


  const style =
    toneStyles[tone]


  return (

    <Card
      className="
        relative
        overflow-hidden
      "
    >

      <div
        className={cn(
          "absolute inset-x-0 top-0 h-px",
          style.border
        )}
      />


      <CardHeader
        className="
          flex-row
          items-center
          justify-between
        "
      >

        <CardTitle
          className="
            text-xs
            font-medium
            uppercase
            tracking-[.14em]
            text-muted-foreground
          "
        >
          {label}
        </CardTitle>


        <Icon
          className={cn(
            "size-4",
            style.icon
          )}
        />


      </CardHeader>



      <CardContent>

        <div
          className="
            flex
            items-end
            justify-between
            gap-4
          "
        >

          <p
            className="
              font-heading
              text-3xl
              font-semibold
              tabular-nums
            "
          >
            {value}
          </p>



          {change && (

            <span
              className={cn(
                "flex items-center text-xs",

                trend === "up"
                  ? style.trendUp
                  : style.trendDown
              )}
            >

              <Trend
                className="size-3"
              />

              {change}

            </span>

          )}


        </div>



        {detail && (

          <p
            className="
              mt-2
              text-xs
              text-muted-foreground
            "
          >
            {detail}
          </p>

        )}


      </CardContent>


    </Card>

  )
}