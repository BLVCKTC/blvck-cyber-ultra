'use client'

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react'

import { API_URL, logoutUrl } from '@/lib/api/config'

export type TenantRole = {
  id: string | null
  key: string | null
  name: string | null
}

export type Membership = {
  tenant_id: string
  role: string
  tenant_role: TenantRole | null
  permissions: string[]
  is_default: boolean
}

export type User = {
  id: string
  email: string | null
  name: string | null
}

export type MeResponse = {
  user: User
  memberships: Membership[]
  default_tenant_id: string | null
  permissions: string[]
}

type AuthState = {
  user: User | null
  memberships: Membership[]
  activeTenant: string | null
  permissions: string[]
  loading: boolean
}

type AuthContextType = AuthState & {
  isAuthenticated: boolean
  refreshUser: () => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

const INITIAL_STATE: Omit<AuthState, 'loading'> = {
  user: null,
  memberships: [],
  activeTenant: null,
  permissions: [],
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    ...INITIAL_STATE,
    loading: true,
  })

  const refreshUser = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
        headers: { Accept: 'application/json' },
      })

      if (!response.ok) {
        throw new Error('Authentication failed')
      }

      const data: MeResponse = await response.json()

      setState({
        user: data.user,
        memberships: data.memberships ?? [],
        activeTenant: data.default_tenant_id ?? null,
        permissions: data.permissions ?? [],
        loading: false,
      })
    } catch (error) {
      setState({ ...INITIAL_STATE, loading: false })
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  const logout = useCallback(async () => {
    setState({ ...INITIAL_STATE, loading: false })
    window.location.href = logoutUrl()
  }, [])

  return (
    <AuthContext.Provider
      value={{
        ...state,
        isAuthenticated: !!state.user,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
