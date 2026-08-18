'use client'

import { createContext, useContext, type ReactNode } from 'react'

export type TenantPermissions = string[]

export type TenantMembership = {
  id: string

  tenant_id: string

  tenant_name: string

  role: string
}

export type TenantContextValue = {
  tenantId: string

  organizationName: string

  tier: string

  role: string

  permissions: TenantPermissions

  /**
   * All tenants the authenticated user belongs to.
   *
   * Sourced from the server-side layout (`/auth/me`) so the client never
   * makes a second request. This is presentation/navigation data only — the
   * server remains the authorization authority for the active tenant.
   */
  memberships: TenantMembership[]
}

const TenantContext = createContext<TenantContextValue | null>(null)

export function TenantProvider({
  value,
  children,
}: {
  value: TenantContextValue
  children: ReactNode
}) {
  return (
    <TenantContext.Provider value={value}>{children}</TenantContext.Provider>
  )
}

export function useTenant() {
  const ctx = useContext(TenantContext)

  if (!ctx) {
    throw new Error('useTenant must be used within TenantProvider')
  }

  return ctx
}
