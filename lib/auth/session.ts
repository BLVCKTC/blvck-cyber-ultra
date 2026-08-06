export async function getCurrentUser() {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
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