'use client'

import { API_URL } from './config'

let refreshPromise: Promise<boolean> | null = null
let logoutRequested = false

const AUTH_REFRESH_PATH = '/auth/refresh'

function devLog(message: string) {
  if (process.env.NODE_ENV !== 'production') console.info(`[AUTH] ${message}`)
}

export function markLogoutRequested() {
  logoutRequested = true
  refreshPromise = null
}

export function resetAuthLifecycle() {
  logoutRequested = false
}

export async function refreshSession(): Promise<boolean> {
  if (logoutRequested) return false
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    devLog('Refresh started')
    try {
      const response = await fetch(`${API_URL}${AUTH_REFRESH_PATH}`, {
        method: 'POST',
        credentials: 'include',
        cache: 'no-store',
        headers: { Accept: 'application/json' },
      })
      if (!response.ok || logoutRequested) {
        devLog('Refresh failed')
        return false
      }
      devLog('Refresh successful')
      return true
    } catch {
      devLog('Refresh unavailable')
      return false
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}

export async function authenticatedFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
): Promise<Response> {
  const request = () => fetch(input, { ...init, credentials: 'include', cache: 'no-store' })
  const response = await request()

  if (response.status !== 401 || logoutRequested) return response
  if (typeof input === 'string' && input.includes(AUTH_REFRESH_PATH)) return response

  if (await refreshSession()) {
    devLog('Retrying request')
    return request()
  }
  return response
}

export async function bestEffortLogout() {
  markLogoutRequested()
  try {
    await fetch(`${API_URL}/auth/logout`, {
      method: 'GET',
      credentials: 'include',
      cache: 'no-store',
      keepalive: true,
    })
  } catch {
    // Local invalidation and navigation must still happen when remote logout is unavailable.
  }
}

export function isLogoutRequested() {
  return logoutRequested
}

export { API_URL }
