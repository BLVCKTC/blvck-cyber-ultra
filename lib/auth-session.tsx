'use client'

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

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
    } catch (error) {
      console.error('AUTH SESSION ERROR:', error)

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
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'GET',

        credentials: 'include',
      })
    } catch (error) {
      console.error('LOGOUT ERROR:', error)
    }

    setUser(null)

    setMemberships([])

    setActiveTenant(null)

    window.location.href = '/login'
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
