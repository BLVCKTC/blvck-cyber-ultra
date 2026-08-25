import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { DashboardShell } from '@/components/soc/shell'
import { TenantProvider } from '@/components/providers/tenant-provider'
import { API_URL } from '@/lib/api/config'

type TenantRole = {
  id: string | null
  key: string | null
  name: string | null
}

type Membership = {
  tenant_id: string
  tenant_name: string | null
  role: string
  tenant_role: TenantRole | null
  permissions: string[]
  is_default: boolean
}

type CurrentUserResponse = {
  user: {
    id: string
    email: string | null
    name: string | null
  }
  memberships: Membership[]
  default_tenant_id: string | null
  permissions: string[]
}

async function getCurrentUser(): Promise<CurrentUserResponse | null> {
  try {
    const cookieStore = await cookies()
    const allCookies = cookieStore.toString()

    if (!allCookies) return null

    const response = await fetch(`${API_URL}/auth/me`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        Cookie: allCookies,
      },
      cache: 'no-store',
    })

    if (!response.ok) return null
    return response.json()
  } catch (error) {
    console.error('Failed to fetch current user:', error)
    return null
  }
}

export default async function DashboardLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params
  const data = await getCurrentUser()

  if (!data) {
    redirect('/login')
  }

  const { user, memberships, default_tenant_id } = data

  const membership = memberships.find((m) => m.tenant_id === tenantId)

  if (!membership) {
    if (default_tenant_id) {
      redirect(`/dashboard/${default_tenant_id}`)
    }
    redirect('/login')
  }

  const tenantMemberships = memberships.map((m) => ({
    id: m.tenant_id,
    tenant_id: m.tenant_id,
    tenant_name: m.tenant_name ?? m.tenant_id,
    role: m.role,
  }))

  const organizationName = membership.tenant_name ?? membership.tenant_id
  const permissions = membership.permissions ?? []

  return (
    <TenantProvider
      value={{
        tenantId: membership.tenant_id,
        organizationName,
        tier: 'enterprise',
        role: membership.role,
        permissions,
        memberships: tenantMemberships,
      }}
    >
      <DashboardShell
        tenantId={membership.tenant_id}
        permissions={permissions}
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
