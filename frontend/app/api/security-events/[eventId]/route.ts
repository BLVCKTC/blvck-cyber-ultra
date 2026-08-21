import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'
import { API_URL } from '@/lib/api/config'

async function getAuthContext() {
  const cookieStore = await cookies()
  return {
    token: cookieStore.get('session_kc_access')?.value,
    tenantId: cookieStore.get('tenant_id')?.value,
  }
}

async function proxyRequest(
  method: 'GET' | 'PATCH' | 'DELETE',
  eventId: string,
  body?: unknown,
) {
  const { token, tenantId } = await getAuthContext()

  if (!token) {
    return NextResponse.json({ detail: 'not_authenticated' }, { status: 401 })
  }

  try {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      Cookie: [
        `session_kc_access=${encodeURIComponent(token)}`,
        tenantId ? `tenant_id=${encodeURIComponent(tenantId)}` : null,
      ]
        .filter(Boolean)
        .join('; '),
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    }

    const response = await fetch(
      `${API_URL}/security-events/${encodeURIComponent(eventId)}`,
      {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        cache: 'no-store',
      },
    )

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 })
    }

    const contentType = response.headers.get('content-type') ?? ''
    const isJson = contentType.includes('application/json')
    const data = isJson ? await response.json() : await response.text()

    return isJson
      ? NextResponse.json(data, { status: response.status })
      : new NextResponse(data, {
          status: response.status,
          headers: { 'Content-Type': contentType || 'text/plain' },
        })
  } catch (error) {
    console.error(`Proxy ${method} failed for event ${eventId}:`, error)
    return NextResponse.json(
      { detail: 'internal_proxy_error' },
      { status: 502 },
    )
  }
}

type RouteContext = {
  params: Promise<{ eventId: string }>
}

export async function GET(_request: NextRequest, { params }: RouteContext) {
  const { eventId } = await params
  return proxyRequest('GET', eventId)
}

export async function PATCH(request: NextRequest, { params }: RouteContext) {
  const { eventId } = await params
  try {
    const body = await request.json()
    return proxyRequest('PATCH', eventId, body)
  } catch {
    return NextResponse.json({ detail: 'invalid_json_body' }, { status: 400 })
  }
}

export async function DELETE(_request: NextRequest, { params }: RouteContext) {
  const { eventId } = await params
  return proxyRequest('DELETE', eventId)
}
