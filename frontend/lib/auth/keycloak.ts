const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"


export function getLoginUrl(
  tenantId: string
) {
  return (
    `${API_URL}/auth/login?tenant_id=${tenantId}`
  )
}