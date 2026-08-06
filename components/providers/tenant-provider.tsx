'use client'

import { createContext, useContext, type ReactNode } from 'react'

export type TenantPermissions = string[]

export type TenantContextValue = {
  tenantId: string

  organizationName: string

  tier: string

  role: string

  permissions: TenantPermissions
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
