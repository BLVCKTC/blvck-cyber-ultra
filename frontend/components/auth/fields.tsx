'use client'

import { useState, type InputHTMLAttributes, type ReactNode } from 'react'
import { Eye, EyeOff } from 'lucide-react'

import { cn } from '@/lib/utils'

/**
 * Themed form primitives for the authentication surface. Palette is scoped
 * locally (explicit hex) to match the AuthShell near-black + electric-blue
 * treatment without touching global theme tokens.
 */

const baseInput =
  'h-11 w-full rounded-md border border-white/10 bg-[#151A21] px-3.5 text-sm text-[#E6EAF0] placeholder:text-[#5B6472] outline-none transition-colors focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/30 disabled:cursor-not-allowed disabled:opacity-60'

export function AuthLabel({
  htmlFor,
  children,
}: {
  htmlFor: string
  children: ReactNode
}) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1.5 block text-xs font-medium text-[#8A93A3]"
    >
      {children}
    </label>
  )
}

export function AuthInput({
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(baseInput, className)} {...props} />
}

export function AuthPasswordInput({
  className,
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="relative">
      <input
        id={id}
        type={visible ? 'text' : 'password'}
        className={cn(baseInput, 'pr-11', className)}
        {...props}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        className="absolute right-0 top-0 flex h-11 w-11 items-center justify-center text-[#5B6472] transition-colors hover:text-[#8A93A3]"
        aria-label={visible ? 'Hide password' : 'Show password'}
        tabIndex={-1}
      >
        {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  )
}

export function AuthPrimaryButton({
  children,
  loading = false,
  className,
  ...props
}: {
  children: ReactNode
  loading?: boolean
} & InputHTMLAttributes<HTMLButtonElement> &
  React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        'group flex h-11 w-full items-center justify-center gap-2 rounded-md bg-[#2563EB] text-sm font-semibold text-white shadow-[0_1px_0_0_rgba(255,255,255,0.08)_inset,0_8px_24px_-8px_rgba(37,99,235,0.6)] transition-all hover:bg-[#1D4FD7] hover:shadow-[0_1px_0_0_rgba(255,255,255,0.08)_inset,0_10px_28px_-8px_rgba(37,99,235,0.75)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB]/50 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none [&_svg]:transition-transform [&:not(:disabled):hover_svg]:translate-x-0.5',
        className,
      )}
      {...props}
    >
      {loading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
      )}
      {children}
    </button>
  )
}

export function AuthErrorBanner({
  title,
  children,
}: {
  title: string
  children?: ReactNode
}) {
  return (
    <div
      role="alert"
      className="rounded-md border border-[#EF4444]/25 bg-[#EF4444]/10 px-3.5 py-3 text-sm text-[#FCA5A5]"
    >
      <p className="font-medium text-[#FCA5A5]">{title}</p>
      {children ? (
        <div className="mt-0.5 text-xs text-[#FCA5A5]/80">{children}</div>
      ) : null}
    </div>
  )
}
