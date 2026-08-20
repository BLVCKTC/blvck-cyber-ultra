'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

import { useAuth } from '@/lib/auth-session'

export default function DashboardEntryPage() {
  const router = useRouter()
  const { loading, isAuthenticated, activeTenant, memberships } = useAuth()

  useEffect(() => {
    if (loading) return

    if (!isAuthenticated) {
      router.replace('/login')
      return
    }

    if (activeTenant) {
      router.replace(`/dashboard/${activeTenant}`)
    }
  }, [loading, isAuthenticated, activeTenant, memberships, router])

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">Checking your session…</main>
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-center text-foreground">
      <section className="max-w-md space-y-3">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">BLVCK CYBER</p>
        <h1 className="text-2xl font-semibold tracking-tight">No organization assigned</h1>
        <p className="text-sm leading-relaxed text-muted-foreground">
          Your account is authenticated, but it does not have access to a security environment yet. Contact your administrator for an invitation.
        </p>
      </section>
    </main>
  )
}
