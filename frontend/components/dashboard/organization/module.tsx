'use client'

import {
  Building2,
  CalendarDays,
  Globe,
  Mail,
  ShieldCheck,
  Users,
  CreditCard,
  Activity,
  LucideIcon,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export type Organization = {
  id: string
  name: string
  slug: string
  website: string | null
  email: string | null
  industry: string | null
  location: string | null
  plan: string
  status: string
  securityScore: number | null
  features: string[]
  created_at: string
  updated_at: string
}

interface OrganizationModuleProps {
  organization: Organization
}

export function OrganizationModule({ organization }: OrganizationModuleProps) {
  const createdDate = new Date(organization.created_at).toLocaleDateString(
    'en-GB',
    {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    },
  )

  const stats = [
    { label: 'Members', value: '—', icon: Users },
    {
      label: 'Security Score',
      value: `${organization.securityScore ?? 0}%`,
      icon: ShieldCheck,
    },
    { label: 'Subscription', value: organization.plan, icon: CreditCard },
    { label: 'Status', value: organization.status, icon: Activity },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
          <Building2 className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Organization</h1>
          <p className="text-sm text-muted-foreground">
            Manage your tenant profile and organization settings
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardContent className="p-5 flex items-center gap-3">
              <Icon className="h-5 w-5 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-xl font-bold">{value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Organization Details</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <Info
              icon={Building2}
              label="Organization Name"
              value={organization.name}
            />
            <Info icon={Globe} label="Website" value={organization.website} />
            <Info icon={Mail} label="Email" value={organization.email} />
          </div>
          <div className="space-y-4">
            <Info icon={CalendarDays} label="Created" value={createdDate} />
            <Info
              icon={Building2}
              label="Industry"
              value={organization.industry}
            />
            <Info icon={Globe} label="Location" value={organization.location} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Enabled Security Capabilities</CardTitle>
        </CardHeader>
        <CardContent>
          {organization.features?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {organization.features.map((feature) => (
                <span
                  key={feature}
                  className="rounded-full border px-3 py-1 text-xs font-medium"
                >
                  {feature}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No security capabilities configured.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function Info({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon
  label: string
  value: string | null
}) {
  return (
    <div className="flex items-center gap-3">
      <Icon className="h-4 w-4 text-muted-foreground" />
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium">{value ?? 'Not configured'}</p>
      </div>
    </div>
  )
}
