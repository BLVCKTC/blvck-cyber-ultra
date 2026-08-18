import { PageHeader } from "@/components/shell/page-header"
import { SalesDashboard } from "@/components/admin/sales-dashboard"

export default function AdminSalesOverviewPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Sales Overview"
        description="Commercial performance across the BLVCK CYBER customer base."
      />
      <div className="p-4 lg:p-6">
        <SalesDashboard />
      </div>
    </div>
  )
}
