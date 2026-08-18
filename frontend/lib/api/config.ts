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
 * Keycloak login is scoped per tenant. The backend's GET /auth/login requires
 * a tenant_id query parameter; this is the ecosystem's default realm/tenant.
 */
export const DEFAULT_TENANT_ID = 'BLVCK-CYBER'

/**
 * Browser navigation target that starts the Keycloak login flow.
 *
 *   /login → GET /api/auth/login?tenant_id=… → Keycloak → /api/auth/callback
 *
 * This MUST be reached with a full browser navigation (window.location.href),
 * never fetch/axios, so the backend 302 redirect chain can complete.
 */
export function loginUrl(tenantId: string = DEFAULT_TENANT_ID): string {
  return `${API_URL}/auth/login?tenant_id=${encodeURIComponent(tenantId)}`
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
