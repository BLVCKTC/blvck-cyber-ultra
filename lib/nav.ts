import {
  LayoutDashboard,
  ShieldAlert,
  Bot,
  Shield,
  Globe,
  Bell,
  Server,
  Crosshair,
  FolderSearch,
  ClipboardCheck,
  FileText,
  Plug,
  Smartphone,
  GraduationCap,
  ShieldCheckIcon,
  Users,
  Settings,
  Building2,
  KeyRound,
  CreditCard,
  UserCog,
  Activity,
  type LucideIcon,
} from 'lucide-react'

export type Permissions = string[]

export type NavItem = {
  title: string
  href: string
  icon: LucideIcon
  badge?: string
  permission?: string
}

export type NavSection = {
  label: string
  items: NavItem[]
}

export function buildNavSections(
  tenantId: string,
  permissions: Permissions = [],
): NavSection[] {
  const base = `/dashboard/${tenantId}`

  const canSee = (item: NavItem) =>
    !item.permission || permissions.includes(item.permission)

  const sections: NavSection[] = [
    {
      label: 'Security Operations',
      items: [
        {
          title: 'Dashboard',
          href: base,
          icon: LayoutDashboard,
        },
        {
          title: 'Alerts',
          href: `${base}/alerts`,
          icon: Bell,
          permission: 'alerts.view',
        },
        {
          title: 'Incidents',
          href: `${base}/incidents`,
          icon: ShieldAlert,
          permission: 'incidents.view',
        },
        {
          title: 'Threat Hunting',
          href: `${base}/hunting`,
          icon: Crosshair,
          permission: 'threatintel.view',
        },
        {
          title: 'Assets',
          href: `${base}/assets`,
          icon: Server,
          permission: 'assets.view',
        },
        {
          title: 'Vulnerabilities',
          href: `${base}/vulnerabilities`,
          icon: ShieldCheckIcon,
          permission: 'vulnerabilities.view',
        },
        {
          title: 'Threat Intelligence',
          href: `${base}/threat-intel`,
          icon: Globe,
          permission: 'threatintel.view',
        },
        {
          title: 'Digital Forensics',
          href: `${base}/forensics`,
          icon: FolderSearch,
          permission: 'forensics.view',
        },
      ],
    },

    {
      label: 'Compliance & Governance',
      items: [
        {
          title: 'Compliance',
          href: `${base}/compliance`,
          icon: ClipboardCheck,
          permission: 'compliance.view',
        },
        {
          title: 'Reports',
          href: `${base}/reports`,
          icon: FileText,
          permission: 'reports.view',
        },
      ],
    },

    {
      label: 'Organization Management',
      items: [
        {
          title: 'Organization',
          href: `${base}/organization`,
          icon: Building2,
          permission: 'organization.view',
        },
        {
          title: 'Users',
          href: `${base}/users`,
          icon: Users,
          permission: 'users.view',
        },
        {
          title: 'Teams',
          href: `${base}/teams`,
          icon: Users,
          permission: 'team.view',
        },
        {
          title: 'Roles & Permissions',
          href: `${base}/roles`,
          icon: Shield,
          permission: 'team.roles.manage',
        },
        {
          title: 'API Keys',
          href: `${base}/api-keys`,
          icon: KeyRound,
          permission: 'apikeys.view',
        },
      ],
    },

    {
      label: 'Identity & Access',
      items: [
        {
          title: 'MFA Policies',
          href: `${base}/mfa`,
          icon: UserCog,
          permission: 'mfa.view',
        },
        {
          title: 'Active Sessions',
          href: `${base}/sessions`,
          icon: Activity,
          permission: 'sessions.view',
        },
      ],
    },

    {
      label: 'Connectivity',
      items: [
        {
          title: 'Integrations',
          href: `${base}/integrations`,
          icon: Plug,
          permission: 'integrations.view',
        },
        {
          title: 'Mobile & PWA',
          href: `${base}/mobile`,
          icon: Smartphone,
        },
      ],
    },

    {
      label: 'Administration',
      items: [
        {
          title: 'Audit Logs',
          href: `${base}/audit`,
          icon: Activity,
          permission: 'audit.view',
        },
        {
          title: 'Settings',
          href: `${base}/settings`,
          icon: Settings,
          permission: 'security.settings.view',
        },
        {
          title: 'Billing',
          href: `${base}/billing`,
          icon: CreditCard,
          permission: 'billing.view',
        },
      ],
    },

    {
      label: 'AI & Automation',
      items: [
        {
          title: 'AI Security Assistant',
          href: `${base}/ai-assistant`,
          icon: Bot,
          permission: 'ai.assistant.use',
        },
        {
          title: 'AI Configuration',
          href: `${base}/ai-config`,
          icon: Bot,
          permission: 'ai.configuration.manage',
        },
      ],
    },

    {
      label: 'Enablement',
      items: [
        {
          title: 'Cyber Academy',
          href: `${base}/academy`,
          icon: GraduationCap,
        },
        {
          title: 'Cyber Insurance',
          href: `${base}/insurance`,
          icon: ShieldCheckIcon,
          badge: 'New',
        },
      ],
    },
  ]

  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter(canSee),
    }))
    .filter((section) => section.items.length > 0)
}
