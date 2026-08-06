import { AttackChart } from '@/components/soc/attack-chart'
import { SecurityScore } from '@/components/soc/security-score'
import { StatCards } from '@/components/soc/stat-cards'
import { ThreatFeed } from '@/components/soc/threat-feed'

export default async function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Security Operations Center</h1>
        <p className="text-muted-foreground">
          Real-time cyber threat monitoring
        </p>
      </div>

      <StatCards />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <AttackChart />
        </div>
        <SecurityScore />
      </div>

      <ThreatFeed />
    </div>
  )
}
