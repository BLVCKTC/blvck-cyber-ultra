import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import {
  OrganizationModule,
  type Organization,
} from '@/components/dashboard/organization/module'
import { API_URL } from '@/lib/api/config'

async function getOrganization(tenantId: string): Promise<Organization | null> {
  try {
    const cookieStore = await cookies()
    const allCookies = cookieStore.toString()

    if (!allCookies) return null

    const response = await fetch(`${API_URL}/tenants/${tenantId}`, {
      headers: {
        Accept: 'application/json',
        Cookie: allCookies,
      },
      cache: 'no-store',
    })

    if (!response.ok) return null

    return response.json()
  } catch (error) {
    return null
  }
}

export default async function OrganizationPage({
  params,
}: {
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params
  const organization = await getOrganization(tenantId)

  if (!organization) {
    redirect(`/dashboard/${tenantId}?error=organization_load_failed`)
  }

  return <OrganizationModule organization={organization} />
}
