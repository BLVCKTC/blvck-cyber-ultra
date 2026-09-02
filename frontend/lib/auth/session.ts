import { API_URL } from '@/lib/api/config'

export async function getCurrentUser() {
  const res = await fetch(
    `${API_URL}/auth/me`,
    {
      credentials: "include",
      cache: "no-store",
    }
  )

  if (!res.ok) {
    return null
  }

  return res.json()
}
