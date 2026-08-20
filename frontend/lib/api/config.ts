// lib/api/config.ts
//
// Single source of truth for talking to the FastAPI backend.
//
// The backend owns authentication (Keycloak / OIDC). The frontend never
// implements its own auth flow — it only redirects the browser to the
// backend's redirect-based endpoints and reads session state from
// GET /auth/me. Keeping the base URL and login/logout URL builders in one
// place avoids hardcoding hosts across the app.

/** Base URL of the FastAPI backend, e.g. http://127.0.0.1:8000/api */
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api'

/**
 * Browser navigation target that starts the Keycloak login flow.
 *
 * Tenant selection is resolved after OIDC authentication from the user's
 * server-side memberships. An optional tenant_id is retained for deep links
 * and invitation flows, but no synthetic tenant is ever sent by default.
 */
export function loginUrl(tenantId?: string | null): string {
  const query = tenantId
    ? `?tenant_id=${encodeURIComponent(tenantId)}`
    : ''

  return `${API_URL}/auth/login${query}`
}

/**
 * Browser navigation target that starts the Keycloak logout flow.
 *
 *   Sign out → GET /api/auth/logout → Keycloak logout → /login
 *
 * Also reached with a full browser navigation so the backend + Keycloak
 * redirect chain completes and every session cookie is cleared server-side.
 */
export function logoutUrl(): string {
  return `${API_URL}/auth/logout`
}
