import { redirect } from 'next/navigation'
import { SettingsModule } from '@/components/dashboard/settings/module'
import { getCurrentUser } from '@/lib/api/auth'

export const metadata = {
  title: 'Settings — BLVCK CYBER',
}

type Membership = {
  tenant_id: string
  role:
    | 'OWNER'
    | 'ADMIN'
    | 'SOC_MANAGER'
    | 'SOC_ANALYST'
    | 'INCIDENT_RESPONDER'
    | 'VIEWER'
  is_default: boolean
}

type CurrentUser = {
  id: number
  email: string | null
  name: string | null
  memberships?: Membership[]
}

export default async function SettingsPage({
  params,
}: {
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params

  const user = (await getCurrentUser()) as CurrentUser | null

  if (!user) {
    redirect('/login')
  }

  const memberships = user.memberships ?? []

  const membership = memberships.find(
    (membership: Membership) => membership.tenant_id === tenantId,
  )

  if (!membership) {
    redirect(`/dashboard/${tenantId}`)
  }

  const allowedRoles = ['OWNER', 'ADMIN']
  const canManageSettings = allowedRoles.includes(membership.role)

  if (!canManageSettings) {
    redirect(`/dashboard/${tenantId}`)
  }

  return <SettingsModule />
}
