// lib/api/auth.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

export type Permission = string

export type AuthUser = {
  id: number
  email: string | null
  name: string | null
}

export type Membership = {
  id: number
  tenant_id: string
  role: string
  tenant_role_id?: number | null
  is_default: boolean
}

export type MeResponse = {
  user: AuthUser
  memberships: Membership[]
  default_tenant_id: string | null
  permissions: Permission[]
}

export async function getCurrentUser(): Promise<MeResponse | null> {
  const res = await fetch(`${API_URL}/auth/me`, {
    credentials: 'include',
    cache: 'no-store',
  })

  if (!res.ok) {
    return null
  }

  return res.json()
}

export async function logout() {
  await fetch(`${API_URL}/auth/logout`, {
    method: 'GET',
    credentials: 'include',
  })
}
