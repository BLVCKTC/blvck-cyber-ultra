'use client'

import { useMemo, useState, type FormEvent } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Check, MailCheck } from 'lucide-react'

import { AuthShell } from '@/components/auth/auth-shell'
import {
  AuthLabel,
  AuthInput,
  AuthPasswordInput,
  AuthPrimaryButton,
  AuthErrorBanner,
} from '@/components/auth/fields'
import { register, AuthError } from '@/lib/api/auth'
import { evaluatePassword, isValidEmail } from '@/lib/auth/password'

type FormState = {
  firstName: string
  lastName: string
  email: string
  password: string
  confirm: string
  organization: string
}

const EMPTY: FormState = {
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirm: '',
  organization: '',
}

export function SignupClient() {
  const router = useRouter()

  const [form, setForm] = useState<FormState>(EMPTY)
  const [agreed, setAgreed] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<{ title: string; hint?: string } | null>(
    null,
  )
  const [success, setSuccess] = useState<null | { verify: boolean }>(null)

  const passwordState = useMemo(
    () => evaluatePassword(form.password),
    [form.password],
  )

  const confirmMatches = form.confirm.length > 0 && form.confirm === form.password

  const canSubmit =
    form.firstName.trim().length > 0 &&
    form.lastName.trim().length > 0 &&
    isValidEmail(form.email) &&
    passwordState.isValid &&
    confirmMatches &&
    form.organization.trim().length > 0 &&
    agreed &&
    !submitting

  function update<K extends keyof FormState>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canSubmit) return

    setSubmitting(true)
    setError(null)

    try {
      const result = await register({
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        email: form.email.trim(),
        password: form.password,
        organization: form.organization.trim(),
        accept_terms: agreed,
      })

      // If the backend logged the user straight in, follow the existing
      // authenticated flow; otherwise show the verify-email success state.
      if (result.authenticated) {
        const target = result.default_tenant_id
          ? `/dashboard/${result.default_tenant_id}`
          : '/dashboard'
        router.replace(target)
        return
      }

      setSuccess({ verify: result.email_verification_required })
    } catch (err) {
      if (err instanceof AuthError) {
        if (err.code === 'email_exists') {
          setError({
            title: 'An account with this email already exists.',
            hint: 'Try signing in instead.',
          })
        } else if (err.code === 'weak_password') {
          setError({
            title: 'Your password does not meet the security requirements.',
          })
        } else if (err.code === 'organization_exists') {
          setError({
            title: 'That organization is already registered.',
            hint: 'Ask an administrator to invite you, or use a different organization name.',
          })
        } else {
          setError({ title: err.message })
        }
      } else {
        setError({ title: "We couldn't create your account. Please try again." })
      }
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <AuthShell>
        <div className="flex flex-col items-start">
          <span className="mb-5 flex h-11 w-11 items-center justify-center rounded-full bg-[#2563EB]/12 ring-1 ring-[#2563EB]/30">
            <MailCheck className="h-5 w-5 text-[#3B82F6]" />
          </span>
          <h1 className="text-2xl font-semibold tracking-tight text-[#E6EAF0]">
            Account created successfully
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-[#8A93A3]">
            We&apos;ve created your BLVCK CYBER account.
            {success.verify
              ? ' Please verify your email before signing in.'
              : ' You can now sign in to your security environment.'}
          </p>

          <div className="mt-8 w-full">
            <Link href="/login">
              <AuthPrimaryButton type="button">Back to sign in</AuthPrimaryButton>
            </Link>
          </div>
        </div>
      </AuthShell>
    )
  }

  return (
    <AuthShell>
      <div className="mb-7">
        <h1 className="text-2xl font-semibold tracking-tight text-[#E6EAF0]">
          Create your account
        </h1>
        <p className="mt-2 text-sm text-[#8A93A3]">
          Set up your BLVCK CYBER account.
        </p>
      </div>

      {error && (
        <div className="mb-5">
          <AuthErrorBanner title={error.title}>
            {error.hint === 'Try signing in instead.' ? (
              <Link href="/login" className="underline hover:text-[#FCA5A5]">
                Try signing in instead.
              </Link>
            ) : (
              error.hint
            )}
          </AuthErrorBanner>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <AuthLabel htmlFor="firstName">First name</AuthLabel>
            <AuthInput
              id="firstName"
              autoComplete="given-name"
              placeholder="Brandon"
              value={form.firstName}
              onChange={(e) => update('firstName', e.target.value)}
              disabled={submitting}
              required
            />
          </div>
          <div>
            <AuthLabel htmlFor="lastName">Last name</AuthLabel>
            <AuthInput
              id="lastName"
              autoComplete="family-name"
              placeholder="Makoni"
              value={form.lastName}
              onChange={(e) => update('lastName', e.target.value)}
              disabled={submitting}
              required
            />
          </div>
        </div>

        <div>
          <AuthLabel htmlFor="email">Work email</AuthLabel>
          <AuthInput
            id="email"
            type="email"
            autoComplete="email"
            inputMode="email"
            placeholder="you@organization.com"
            value={form.email}
            onChange={(e) => update('email', e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        <div>
          <AuthLabel htmlFor="organization">Organization</AuthLabel>
          <AuthInput
            id="organization"
            autoComplete="organization"
            placeholder="Your organization name"
            value={form.organization}
            onChange={(e) => update('organization', e.target.value)}
            disabled={submitting}
            required
          />
          <p className="mt-1.5 text-[11px] text-[#5B6472]">
            Your account will be created as the owner of this organization.
          </p>
        </div>

        <div>
          <AuthLabel htmlFor="password">Password</AuthLabel>
          <AuthPasswordInput
            id="password"
            autoComplete="new-password"
            placeholder="Create a strong password"
            value={form.password}
            onChange={(e) => update('password', e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        {/* Dynamic password requirements */}
        {form.password.length > 0 && (
          <div className="rounded-md border border-white/8 bg-[#0D1117] px-3.5 py-3">
            <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.18em] text-[#5B6472]">
              Password requirements
            </p>
            <ul className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
              {passwordState.results.map((rule) => (
                <li
                  key={rule.id}
                  className="flex items-center gap-2 text-xs"
                >
                  <span
                    className={
                      rule.passed
                        ? 'flex h-3.5 w-3.5 items-center justify-center rounded-full bg-[#2563EB]/20 text-[#3B82F6]'
                        : 'flex h-3.5 w-3.5 items-center justify-center rounded-full border border-white/15 text-transparent'
                    }
                  >
                    <Check className="h-2.5 w-2.5" />
                  </span>
                  <span
                    className={rule.passed ? 'text-[#8A93A3]' : 'text-[#5B6472]'}
                  >
                    {rule.label}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <AuthLabel htmlFor="confirm">Confirm password</AuthLabel>
          <AuthPasswordInput
            id="confirm"
            autoComplete="new-password"
            placeholder="Re-enter your password"
            value={form.confirm}
            onChange={(e) => update('confirm', e.target.value)}
            disabled={submitting}
            required
          />
          {form.confirm.length > 0 && !confirmMatches && (
            <p className="mt-1.5 text-[11px] text-[#FCA5A5]">
              Passwords do not match.
            </p>
          )}
        </div>

        <label className="flex cursor-pointer items-start gap-2.5 pt-1 text-xs leading-relaxed text-[#8A93A3]">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            disabled={submitting}
            className="mt-0.5 h-3.5 w-3.5 rounded border-white/20 bg-[#151A21] accent-[#2563EB]"
          />
          <span>
            I agree to the{' '}
            <a href="/legal/terms" className="text-[#3B82F6] hover:text-[#60A5FA]">
              Terms of Service
            </a>{' '}
            and{' '}
            <a
              href="/legal/privacy"
              className="text-[#3B82F6] hover:text-[#60A5FA]"
            >
              Privacy Policy
            </a>
            .
          </span>
        </label>

        <div className="pt-2">
          <AuthPrimaryButton type="submit" loading={submitting} disabled={!canSubmit}>
            {submitting ? 'Creating your account…' : 'Create account'}
          </AuthPrimaryButton>
        </div>
      </form>

      <p className="mt-8 text-center text-sm text-[#8A93A3]">
        Already have an account?{' '}
        <Link
          href="/login"
          className="font-medium text-[#3B82F6] transition-colors hover:text-[#60A5FA]"
        >
          Sign in
        </Link>
      </p>
    </AuthShell>
  )
}
