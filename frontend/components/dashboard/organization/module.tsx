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
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const mockOrganization = {
  id: 'BLVCK-CYBER',
  name: 'BLVCK Cyber Technologies',
  industry: 'Cybersecurity',
  website: 'https://blvckcyber.com',
  email: 'admin@blvckcyber.com',
  plan: 'Enterprise',
  status: 'Active',
  createdAt: '06 August 2026',

  securityScore: 94,
  members: 42,

  location: 'South Africa',

  features: [
    'AI Threat Detection',
    'Threat Intelligence',
    'Digital Forensics',
    'Security Monitoring',
    'Compliance Management',
  ],
}

export function OrganizationModule() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div
          className="
            flex h-12 w-12
            items-center justify-center
            rounded-xl
            bg-primary/10
          "
        >
          <Building2 className="h-6 w-6 text-primary" />
        </div>

        <div>
          <h1 className="text-2xl font-bold">Organization</h1>

          <p className="text-sm text-muted-foreground">
            Manage your tenant profile and organization settings
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Members</p>

                <p className="text-xl font-bold">{mockOrganization.members}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <ShieldCheck className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Security Score</p>

                <p className="text-xl font-bold">
                  {mockOrganization.securityScore}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <CreditCard className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Subscription</p>

                <p className="text-xl font-bold">{mockOrganization.plan}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Status</p>

                <p className="text-xl font-bold">{mockOrganization.status}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Organization Details */}
      <Card>
        <CardHeader>
          <CardTitle>Organization Details</CardTitle>
        </CardHeader>

        <CardContent className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <Info
              icon={<Building2 />}
              label="Organization Name"
              value={mockOrganization.name}
            />

            <Info
              icon={<Globe />}
              label="Website"
              value={mockOrganization.website}
            />

            <Info
              icon={<Mail />}
              label="Email"
              value={mockOrganization.email}
            />
          </div>

          <div className="space-y-4">
            <Info
              icon={<CalendarDays />}
              label="Created"
              value={mockOrganization.createdAt}
            />

            <Info
              icon={<Building2 />}
              label="Industry"
              value={mockOrganization.industry}
            />

            <Info
              icon={<Globe />}
              label="Location"
              value={mockOrganization.location}
            />
          </div>
        </CardContent>
      </Card>

      {/* Enabled Features */}
      <Card>
        <CardHeader>
          <CardTitle>Enabled Security Capabilities</CardTitle>
        </CardHeader>

        <CardContent>
          <div className="flex flex-wrap gap-2">
            {mockOrganization.features.map((feature) => (
              <span
                key={feature}
                className="
                  rounded-full
                  border
                  px-3
                  py-1
                  text-xs
                  font-medium
                "
              >
                {feature}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function Info({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="text-muted-foreground">{icon}</div>

      <div>
        <p className="text-xs text-muted-foreground">{label}</p>

        <p className="text-sm font-medium">{value}</p>
      </div>
    </div>
  )
}
