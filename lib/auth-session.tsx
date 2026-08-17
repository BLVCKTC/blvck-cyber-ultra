'use client'

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

import { API_URL, logoutUrl } from '@/lib/api/config'

export type Membership = {
  tenant_id: string

  role: string

  tenant_role?: {
    id: number

    key: string

    name: string
  }

  permissions: string[]

  is_default: boolean
}

export type User = {
  id: number

  email: string

  name: string | null
}

export type MeResponse = {
  user: User

  memberships: Membership[]

  default_tenant_id: string | null
}

type AuthContextType = {
  user: User | null

  memberships: Membership[]

  activeTenant: string | null

  loading: boolean

  isAuthenticated: boolean

  refreshUser: () => Promise<void>

  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  const [memberships, setMemberships] = useState<Membership[]>([])

  const [activeTenant, setActiveTenant] = useState<string | null>(null)

  const [loading, setLoading] = useState(true)

  async function refreshUser() {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        method: 'GET',

        credentials: 'include',

        cache: 'no-store',

        headers: {
          Accept: 'application/json',
        },
      })

      if (!response.ok) {
        setUser(null)

        setMemberships([])

        setActiveTenant(null)

        return
      }

      const data: MeResponse = await response.json()

      setUser(data.user)

      setMemberships(data.memberships ?? [])

      setActiveTenant(data.default_tenant_id)
    } catch {
      // A failed /auth/me probe (network error, or the backend unreachable)
      // is treated as "not authenticated" — the same as a 401. This is a
      // normal condition on the login screen, so we don't raise a scary
      // error; we simply clear any session state.
      setUser(null)

      setMemberships([])

      setActiveTenant(null)
    }
  }

  useEffect(() => {
    refreshUser().finally(() => {
      setLoading(false)
    })
  }, [])

  async function logout() {
    // 1. Clear client-side auth state immediately so no stale authenticated
    //    UI can be rendered while the browser navigates away. This also
    //    prevents returning to a protected page via stale React state.
    setUser(null)
    setMemberships([])
    setActiveTenant(null)

    // 2. Hand control to the backend's redirect-based logout. A full browser
    //    navigation is required (NOT fetch) so the backend + Keycloak 302
    //    redirect chain can complete and every session cookie is cleared
    //    server-side. Keycloak ultimately redirects back to /login, where
    //    GET /auth/me returns 401 and the login screen is shown.
    window.location.href = logoutUrl()
  }

  return (
    <AuthContext.Provider
      value={{
        user,

        memberships,

        activeTenant,

        loading,

        isAuthenticated: !!user,

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
