'use client'

import { useState, type FormEvent } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { AuthShell } from '@/components/auth/auth-shell'
import {
  AuthLabel,
  AuthInput,
  AuthPasswordInput,
  AuthPrimaryButton,
  AuthErrorBanner,
} from '@/components/auth/fields'
import { login, AuthError } from '@/lib/api/auth'
import { isValidEmail } from '@/lib/auth/password'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

export function LoginClient() {
  const router = useRouter()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSubmit = isValidEmail(email) && password.length > 0 && !submitting

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canSubmit) return

    setSubmitting(true)
    setError(null)

    try {
      const { default_tenant_id } = await login({
        email: email.trim(),
        password,
        remember,
      })

      // The backend is the sole authority for tenant scope; we only navigate
      // to whatever default it returns (falling back to /dashboard).
      const target = default_tenant_id
        ? `/dashboard/${default_tenant_id}`
        : '/dashboard'
      router.replace(target)
    } catch (err) {
      if (err instanceof AuthError) {
        setError(err.message)
      } else {
        setError('We could not sign you in. Please try again.')
      }
      setSubmitting(false)
    }
  }

  return (
    <AuthShell>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-[#E6EAF0]">
          Welcome back.
        </h1>
        <p className="mt-2 text-sm text-[#8A93A3]">
          Sign in to your security operations environment.
        </p>
      </div>

      {error && (
        <div className="mb-5">
          <AuthErrorBanner title={error} />
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <AuthLabel htmlFor="email">Work email</AuthLabel>
          <AuthInput
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            inputMode="email"
            placeholder="you@organization.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        <div>
          <AuthLabel htmlFor="password">Password</AuthLabel>
          <AuthPasswordInput
            id="password"
            name="password"
            autoComplete="current-password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        <div className="flex items-center justify-between pt-1">
          <label className="flex cursor-pointer items-center gap-2 text-xs text-[#8A93A3]">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              disabled={submitting}
              className="h-3.5 w-3.5 rounded border-white/20 bg-[#151A21] accent-[#2563EB]"
            />
            Remember me
          </label>

          <a
            href={`${API_URL}/auth/forgot-password`}
            className="text-xs text-[#3B82F6] transition-colors hover:text-[#60A5FA]"
          >
            Forgot password?
          </a>
        </div>

        <div className="pt-2">
          <AuthPrimaryButton type="submit" loading={submitting} disabled={!canSubmit}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </AuthPrimaryButton>
        </div>
      </form>

      <p className="mt-8 text-center text-sm text-[#8A93A3]">
        Don&apos;t have an account?{' '}
        <Link
          href="/signup"
          className="font-medium text-[#3B82F6] transition-colors hover:text-[#60A5FA]"
        >
          Create an account
        </Link>
      </p>
    </AuthShell>
  )
}
