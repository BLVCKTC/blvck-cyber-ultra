// lib/auth/password.ts

/**
 * Client-side password policy used to guide the user and to prevent obviously
 * invalid submissions. The backend re-validates every rule server-side — this
 * is a UX aid, never the security boundary.
 */

export type PasswordRuleId =
  | 'length'
  | 'uppercase'
  | 'lowercase'
  | 'number'
  | 'special'

export type PasswordRule = {
  id: PasswordRuleId
  label: string
  test: (value: string) => boolean
}

export const PASSWORD_RULES: PasswordRule[] = [
  {
    id: 'length',
    label: 'At least 8 characters',
    test: (v) => v.length >= 8,
  },
  {
    id: 'uppercase',
    label: 'One uppercase letter',
    test: (v) => /[A-Z]/.test(v),
  },
  {
    id: 'lowercase',
    label: 'One lowercase letter',
    test: (v) => /[a-z]/.test(v),
  },
  {
    id: 'number',
    label: 'One number',
    test: (v) => /[0-9]/.test(v),
  },
  {
    id: 'special',
    label: 'One special character',
    test: (v) => /[^A-Za-z0-9]/.test(v),
  },
]

export function evaluatePassword(value: string) {
  const results = PASSWORD_RULES.map((rule) => ({
    id: rule.id,
    label: rule.label,
    passed: rule.test(value),
  }))

  const passedCount = results.filter((r) => r.passed).length

  return {
    results,
    passedCount,
    total: PASSWORD_RULES.length,
    isValid: passedCount === PASSWORD_RULES.length,
  }
}

export function isValidEmail(value: string) {
  // Pragmatic RFC-5322-ish check; backend performs authoritative validation.
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())
}
