// lib/api/auth.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

export type Permission = string

export type AuthUser = {
  id: number
  email: string | null
  name: string | null
}

export type Membership = {
  id: number
  tenant_id: string
  role: string
  tenant_role_id?: number | null
  is_default: boolean
}

export type MeResponse = {
  user: AuthUser
  memberships: Membership[]
  default_tenant_id: string | null
  permissions: Permission[]
}

export async function getCurrentUser(): Promise<MeResponse | null> {
  const res = await fetch(`${API_URL}/auth/me`, {
    credentials: 'include',
    cache: 'no-store',
  })

  if (!res.ok) {
    return null
  }

  return res.json()
}

export async function logout() {
  await fetch(`${API_URL}/auth/logout`, {
    method: 'GET',
    credentials: 'include',
  })
}

/* -------------------------------------------------------------------------- */
/*  Structured auth errors                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Stable, UI-facing error codes. These are derived from the backend HTTP
 * status / error body so that the UI can render precise, safe messages
 * without ever surfacing a raw backend exception.
 */
export type AuthErrorCode =
  | 'invalid_credentials'
  | 'email_exists'
  | 'weak_password'
  | 'organization_exists'
  | 'validation'
  | 'rate_limited'
  | 'unavailable'
  | 'unknown'

export class AuthError extends Error {
  code: AuthErrorCode

  constructor(code: AuthErrorCode, message: string) {
    super(message)
    this.name = 'AuthError'
    this.code = code
  }
}

/**
 * Best-effort extraction of a backend-provided error code without ever
 * exposing raw exception text to the user. We only read a small, known set
 * of fields the backend may return.
 */
function parseErrorBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return null
  const record = body as Record<string, unknown>
  const candidate = record.code ?? record.error ?? record.detail
  return typeof candidate === 'string' ? candidate.toLowerCase() : null
}

async function readJsonSafe(res: Response): Promise<unknown> {
  try {
    return await res.json()
  } catch {
    return null
  }
}

/* -------------------------------------------------------------------------- */
/*  Login (email + password -> backend -> Keycloak)                            */
/* -------------------------------------------------------------------------- */

export type LoginRequest = {
  email: string
  password: string
  remember?: boolean
}

export type LoginResult = {
  default_tenant_id: string | null
}

/**
 * Posts credentials to the backend, which authenticates against Keycloak and
 * sets the httpOnly session cookie. The browser never stores tokens itself.
 */
export async function login(input: LoginRequest): Promise<LoginResult> {
  let res: Response
  try {
    res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      credentials: 'include',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        email: input.email,
        password: input.password,
        remember: input.remember ?? false,
      }),
    })
  } catch {
    throw new AuthError('unavailable', 'We could not reach the sign-in service.')
  }

  if (res.ok) {
    const data = (await readJsonSafe(res)) as Partial<LoginResult> | null
    return { default_tenant_id: data?.default_tenant_id ?? null }
  }

  if (res.status === 401 || res.status === 403) {
    throw new AuthError('invalid_credentials', 'Incorrect email or password.')
  }
  if (res.status === 429) {
    throw new AuthError('rate_limited', 'Too many attempts. Please wait and try again.')
  }
  if (res.status >= 500) {
    throw new AuthError('unavailable', 'The sign-in service is temporarily unavailable.')
  }

  throw new AuthError('unknown', 'We could not sign you in. Please try again.')
}

/* -------------------------------------------------------------------------- */
/*  Register (form -> backend -> Keycloak + DB + tenant + membership)          */
/* -------------------------------------------------------------------------- */

export type RegisterRequest = {
  first_name: string
  last_name: string
  email: string
  password: string
  organization: string
  /** Confirmation the user accepted Terms + Privacy. Backend re-validates. */
  accept_terms: boolean
}

export type RegisterResult = {
  /** True when Keycloak requires email verification before first sign-in. */
  email_verification_required: boolean
  /** True when the backend established a session and the user may proceed. */
  authenticated: boolean
  default_tenant_id: string | null
}

/**
 * Submits the registration to the backend. The backend is solely responsible
 * for creating the Keycloak identity, the application user, the tenant, and
 * the initial membership/role. The frontend never sends tenant_id, role,
 * permissions, or user_id — those are determined server-side.
 */
export async function register(input: RegisterRequest): Promise<RegisterResult> {
  let res: Response
  try {
    res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      credentials: 'include',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        first_name: input.first_name,
        last_name: input.last_name,
        email: input.email,
        password: input.password,
        organization: input.organization,
        accept_terms: input.accept_terms,
      }),
    })
  } catch {
    throw new AuthError('unavailable', "We couldn't create your account. Please try again.")
  }

  if (res.ok) {
    const data = (await readJsonSafe(res)) as Partial<RegisterResult> | null
    return {
      email_verification_required: data?.email_verification_required ?? true,
      authenticated: data?.authenticated ?? false,
      default_tenant_id: data?.default_tenant_id ?? null,
    }
  }

  const code = parseErrorBody(await readJsonSafe(res))

  if (res.status === 409 || code === 'email_exists' || code === 'email_taken') {
    throw new AuthError('email_exists', 'An account with this email already exists.')
  }
  if (code === 'organization_exists') {
    throw new AuthError('organization_exists', 'That organization is already registered.')
  }
  if (res.status === 422 || code === 'weak_password') {
    if (code === 'weak_password') {
      throw new AuthError(
        'weak_password',
        'Your password does not meet the security requirements.',
      )
    }
    throw new AuthError('validation', 'Please check your details and try again.')
  }
  if (res.status === 400) {
    throw new AuthError('validation', 'Please check your details and try again.')
  }
  if (res.status === 429) {
    throw new AuthError('rate_limited', 'Too many attempts. Please wait and try again.')
  }
  if (res.status >= 500) {
    throw new AuthError('unavailable', "We couldn't create your account. Please try again.")
  }

  throw new AuthError('unknown', "We couldn't create your account. Please try again.")
}
