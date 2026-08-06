import { PageHeader } from "@/components/shell/page-header"
import { AIGrowthPrediction } from "@/components/admin/ai-growth-prediction"

export default function GrowthIntelligencePage() {
  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Growth Intelligence"
        description="AI-driven revenue forecasting, customer churn prediction and growth opportunities for BLVCK CYBER."
      />

      <div className="p-4 lg:p-6">
        <AIGrowthPrediction />
      </div>
    </div>
  )
}
