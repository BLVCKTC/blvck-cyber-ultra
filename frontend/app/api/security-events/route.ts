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

async function proxyRequest(method: string, endpoint: string, body?: unknown) {
  const { token, tenantId } = await getAuthContext()

  if (!token) {
    return NextResponse.json({ detail: 'not_authenticated' }, { status: 401 })
  }

  try {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    }

    if (tenantId) {
      headers['Cookie'] = `tenant_id=${tenantId}`
    }

    if (body) {
      headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      cache: 'no-store',
    })

    const contentType = response.headers.get('content-type') ?? ''
    const isJson = contentType.includes('application/json')
    const data = isJson ? await response.json() : await response.text()

    return new NextResponse(isJson ? JSON.stringify(data) : data, {
      status: response.status,
      headers: { 'Content-Type': contentType || 'text/plain' },
    })
  } catch (error) {
    return NextResponse.json(
      { detail: 'internal_proxy_error' },
      { status: 502 },
    )
  }
}

export async function GET(request: NextRequest) {
  return proxyRequest('GET', `/security-events${request.nextUrl.search}`)
}

export async function PATCH(request: NextRequest) {
  const eventId = request.nextUrl.searchParams.get('eventId')
  if (!eventId) {
    return NextResponse.json({ detail: 'eventId is required' }, { status: 400 })
  }

  try {
    const body = await request.json()
    return proxyRequest(
      'PATCH',
      `/security-events/${encodeURIComponent(eventId)}`,
      body,
    )
  } catch {
    return NextResponse.json({ detail: 'invalid_json_body' }, { status: 400 })
  }
}

export async function DELETE(request: NextRequest) {
  const eventId = request.nextUrl.searchParams.get('eventId')
  if (!eventId) {
    return NextResponse.json({ detail: 'eventId is required' }, { status: 400 })
  }

  return proxyRequest(
    'DELETE',
    `/security-events/${encodeURIComponent(eventId)}`,
  )
}
