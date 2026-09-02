import { API_URL } from '@/lib/api/config'

export function getLoginUrl(
  tenantId: string
) {
  return (
    `${API_URL}/auth/login?tenant_id=${tenantId}`
  )
}
