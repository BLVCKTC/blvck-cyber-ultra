import { PageHeader } from '@/components/shell/page-header'
import { Simulator } from '@/components/soc/simulator'

export default function SocDemoPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Interactive Demo"
        title="AI-SOC Demo Simulator"
        description="Experience how the BLVCK CYBER autonomous SOC detects, investigates, and contains a live attack — then export a full incident report as a PDF."
      />
      <Simulator />
    </div>
  )
}
