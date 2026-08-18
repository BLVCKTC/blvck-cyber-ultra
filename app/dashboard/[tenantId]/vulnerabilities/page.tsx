import { SectionHeading } from '@/components/soc/shell'
import { VulnerabilitiesView } from '@/components/soc/vulnerabilities/vulnerabilities-view'
import { vulnerabilities } from '@/lib/soc/mock'

export const metadata = { title: 'Vulnerabilities — BLVCK CYBER' }

export default async function VulnerabilitiesPage() {
  const open = vulnerabilities.filter(
    (v) => v.status === 'open' || v.status === 'in_progress',
  ).length
  const exploitable = vulnerabilities.filter(
    (v) => v.exploitAvailable && v.status !== 'remediated',
  ).length

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Vulnerabilities"
        sub={`${open} unresolved · ${exploitable} with known exploits · prioritized by exposure and exploitability.`}
      />
      <VulnerabilitiesView />
    </div>
  )
}
