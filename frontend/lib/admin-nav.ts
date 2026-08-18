import {
  BarChart3,
  Users,
  UserRoundCheck,
  HeartPulse,
  Handshake,
  TrendingUp,
  type LucideIcon,
} from 'lucide-react'

export type AdminNavItem = {
  title: string
  href: string
  icon: LucideIcon
  badge?: string
}

// Admin-only navigation — exactly 6 pages, by design. Anything else
// (Revenue Analytics, etc.) belongs on the customer-facing side, not
// here. Only ever rendered inside app/admin's own layout — never
// merged with or imported by the customer-facing sidebar (lib/nav.ts).
export const adminNavItems: AdminNavItem[] = [
  { title: 'Sales Overview', href: '/admin', icon: BarChart3 },
  { title: 'Leads Pipeline', href: '/admin/leads', icon: Users },
  { title: 'Subscribers', href: '/admin/subscribers', icon: UserRoundCheck },
  { title: 'Subscription Health', href: '/admin/subscription-health', icon: HeartPulse },
  { title: 'Partner Portal', href: '/admin/partners', icon: Handshake },
  { title: 'Growth Intelligence', href: '/admin/growth', icon: TrendingUp, badge: 'AI' },
]