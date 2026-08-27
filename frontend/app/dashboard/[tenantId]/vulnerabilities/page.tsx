import { SectionHeading } from '@/components/soc/shell'
import { VulnerabilitiesView } from '@/components/soc/vulnerabilities/vulnerabilities-view'
export const metadata = { title: 'Vulnerabilities — BLVCK CYBER' }

export default function VulnerabilitiesPage() {
  return (
    <div className="space-y-6">
      <SectionHeading
        title="Vulnerabilities"
        sub="Tenant findings prioritized by exposure, exploitability, and remediation status."
      />
      <VulnerabilitiesView />
    </div>
  )
}
