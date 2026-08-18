import { NextResponse } from 'next/server'

import { logoutUrl } from '@/lib/api/config'

// Server-side logout entry point (used e.g. by the admin sidebar link).
// Hands off to the backend's redirect-based logout so the Keycloak logout
// chain completes and ends back on /login.
export async function GET() {
  return NextResponse.redirect(logoutUrl())
}
