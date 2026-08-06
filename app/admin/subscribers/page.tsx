import { PageHeader } from "@/components/shell/page-header"
import { SubscriberManagement } from "@/components/admin/subscriber-management"

export default function SubscribersPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Subscriber Management"
        description="Monitor every BLVCK CYBER account, filter by plan and status, and drill into individual subscribers for health, billing, and security posture."
      />
      <SubscriberManagement />
    </div>
  )
}
