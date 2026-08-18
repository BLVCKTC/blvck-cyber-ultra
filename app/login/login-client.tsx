'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowRight, ShieldCheck } from 'lucide-react'

import { AuthShell } from '@/components/auth/auth-shell'
import { AuthPrimaryButton, AuthErrorBanner } from '@/components/auth/fields'
import { useAuth } from '@/lib/auth-session'
import { loginUrl } from '@/lib/api/config'

/**
 * BLVCK CYBER sign-in.
 *
 * Authentication is owned by the backend (Keycloak / OIDC). This screen never
 * collects a password or POSTs credentials. It:
 *   1. Reads session state from the shared AuthProvider (GET /auth/me).
 *   2. Redirects an already-authenticated user straight to their dashboard.
 *   3. Starts the Keycloak flow with a full browser navigation to
 *      GET /api/auth/login?tenant_id=… when the user clicks sign in.
 */
export function LoginClient() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { loading, isAuthenticated, activeTenant } = useAuth()

  const [connecting, setConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Surface a useful message if the backend/Keycloak redirected back with an
  // error (e.g. /login?error=…). A normal unauthenticated visit has no param
  // and shows no scary error.
  useEffect(() => {
    const code = searchParams.get('error')
    if (!code) return
    if (code === 'session_expired') {
      setError('Your session expired. Please sign in again.')
    } else {
      setError('We could not complete sign-in. Please try again.')
    }
  }, [searchParams])

  // Already authenticated → send to the dashboard, don't show the login page.
  useEffect(() => {
    if (loading || !isAuthenticated) return
    const target = activeTenant ? `/dashboard/${activeTenant}` : '/dashboard'
    router.replace(target)
  }, [loading, isAuthenticated, activeTenant, router])

  function handleSignIn() {
    if (connecting) return // prevent duplicate clicks
    setConnecting(true)
    setError(null)
    try {
      // Full browser navigation so the backend 302 → Keycloak redirect
      // chain can complete. Never fetch/POST this endpoint.
      window.location.href = loginUrl()
    } catch {
      setConnecting(false)
      setError(
        'The authentication service is unavailable. Please try again shortly.',
      )
    }
  }

  // While the initial session check runs, or while an authenticated user is
  // being redirected away, show a calm interstitial instead of flashing the
  // sign-in form.
  if (loading || isAuthenticated) {
    return (
      <AuthShell>
        <div
          className="flex items-center gap-3 text-sm text-[#8A93A3]"
          role="status"
          aria-live="polite"
        >
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#2563EB]/30 border-t-[#3B82F6]" />
          {isAuthenticated
            ? 'Loading your environment…'
            : 'Checking your session…'}
        </div>
      </AuthShell>
    )
  }

  return (
    <AuthShell>
      <div className="mb-8">
        <p className="mb-3 font-mono text-[11px] tracking-[0.22em] text-[#5B6472]">
          SECURITY OPERATIONS
        </p>
        <h1 className="text-2xl font-semibold tracking-tight text-balance text-[#E6EAF0]">
          Welcome back.
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-pretty text-[#8A93A3]">
          Sign in to your BLVCK CYBER security operations environment.
        </p>
      </div>

      {error && (
        <div className="mb-5">
          <AuthErrorBanner title={error} />
        </div>
      )}

      <AuthPrimaryButton
        type="button"
        onClick={handleSignIn}
        loading={connecting}
        disabled={connecting}
        aria-label="Sign in to BLVCK CYBER with BLVCK ID"
      >
        {connecting ? (
          'Connecting to BLVCK ID…'
        ) : (
          <>
            Sign in to BLVCK CYBER
            <ArrowRight className="h-4 w-4" aria-hidden />
          </>
        )}
      </AuthPrimaryButton>

      <p className="mt-4 flex items-center gap-2 text-xs leading-relaxed text-[#5B6472]">
        <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-[#3B82F6]/70" aria-hidden />
        Authenticated securely with BLVCK ID · Single sign-on
      </p>

      <p className="mt-8 text-sm text-[#8A93A3]">
        Don&apos;t have a BLVCK account?{' '}
        <Link
          href="/signup"
          className="font-medium text-[#3B82F6] underline-offset-4 transition-colors hover:text-[#60A5FA] focus:outline-none focus-visible:underline"
        >
          Create an account
        </Link>
      </p>

      <div className="mt-12 border-t border-white/5 pt-5">
        <p className="text-xs text-[#5B6472]">
          BLVCK Systems Africa
          <span className="mx-1.5 text-[#2A313B]">·</span>
          <span className="font-mono">© 2026</span>
        </p>
      </div>
    </AuthShell>
  )
}
