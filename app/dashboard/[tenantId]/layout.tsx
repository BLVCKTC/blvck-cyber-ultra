import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { DashboardShell } from '@/components/soc/shell'
import { TenantProvider } from '@/components/providers/tenant-provider'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

async function getCurrentUser() {
  const cookieStore = await cookies()

  const session = cookieStore.get('session_kc_access')

  if (!session) {
    return null
  }

  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      Cookie: `${session.name}=${session.value}`,
    },
    cache: 'no-store',
  })

  if (!response.ok) {
    return null
  }

  return response.json()
}

export default async function DashboardLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{
    tenantId: string
  }>
}) {
  const { tenantId } = await params

  const data = await getCurrentUser()

  if (!data) {
    redirect('/login')
  }

  const { user, memberships, default_tenant_id } = data

  const membership = memberships.find((m: any) => m.tenant_id === tenantId)

  if (!membership) {
    if (default_tenant_id) {
      redirect(`/dashboard/${default_tenant_id}`)
    }

    redirect('/login')
  }

  return (
    <TenantProvider
      value={{
        tenantId: membership.tenant_id,

        organizationName: membership.tenant_id,

        tier: 'enterprise',

        permissions: membership.permissions ?? [],

        role: membership.role,
      }}
    >
      <DashboardShell
        tenantId={membership.tenant_id}
        permissions={membership.permissions ?? []}
        user={{
          id: user.id,

          name: user.name,

          email: user.email,

          role: membership.role,

          tenantId: membership.tenant_id,
        }}
      >
        {children}
      </DashboardShell>
    </TenantProvider>
  )
}
