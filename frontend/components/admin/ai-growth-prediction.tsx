"use client"

import {
  Brain,
  TrendingUp,
  AlertTriangle,
  Users,
  DollarSign,
} from "lucide-react"

import { StatCard } from "@/components/shell/stat-card"


export function AIGrowthPrediction() {

  return (
    <div className="space-y-6">


      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">

        <StatCard
          label="Q3 Revenue Forecast"
          value="$482K"
          change="+18% projected"
          tone="success"
          icon={TrendingUp}
        />


        <StatCard
          label="Customer Churn Risk"
          value="7.4%"
          tone="warning"
          icon={AlertTriangle}
        />


        <StatCard
          label="Upsell Opportunities"
          value="23"
          tone="cyber"
          icon={Users}
        />


        <StatCard
          label="AI Confidence"
          value="91%"
          tone="success"
          icon={Brain}
        />

      </div>



      <div className="grid lg:grid-cols-2 gap-6">


        <div className="glass p-6">

          <div className="flex items-center gap-2 mb-4">

            <DollarSign className="h-5 w-5 text-cyber"/>

            <h2 className="font-display font-bold">
              Revenue Prediction
            </h2>

          </div>


          <div className="text-5xl font-bold">
            $482,000
          </div>


          <p className="text-sm text-muted-foreground mt-3">
            AI forecast based on:
          </p>


          <ul className="mt-4 space-y-2 text-sm">

            <li>
              • Sales pipeline conversion
            </li>

            <li>
              • Subscription renewal probability
            </li>

            <li>
              • Historical growth trends
            </li>

          </ul>

        </div>



        <div className="glass p-6">


          <div className="flex items-center gap-2 mb-4">

            <AlertTriangle className="h-5 w-5 text-warning"/>

            <h2 className="font-display font-bold">
              Churn Prediction
            </h2>

          </div>



          <Risk
            company="KCB Kenya"
            reason="Security score decreasing"
          />


          <Risk
            company="MTN Ghana"
            reason="Low platform usage"
          />


          <Risk
            company="First Bank Nigeria"
            reason="Payment behaviour change"
          />


        </div>

      </div>


    </div>
  )
}



function Risk({
 company,
 reason
}:{
 company:string
 reason:string
}){

return (

<div className="bg-black/40 rounded-lg p-3 mb-3">

<div className="font-medium">
{company}
</div>

<div className="text-xs text-warning">
{reason}
</div>

</div>

)

}