'use client'

import { useState } from 'react'

import {
  ShieldCheck,
  Smartphone,
  Mail,
  KeyRound,
  Lock,
  Users,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

import { Button } from '@/components/ui/button'

import { Badge } from '@/components/ui/badge'

type MFASettings = {
  enforced: boolean
  methods: string[]
  recoveryCodes: boolean
  trustedDevices: boolean
}

const MOCK_MFA: MFASettings = {
  enforced: true,

  methods: ['Authenticator App', 'Email OTP', 'Security Key'],

  recoveryCodes: true,

  trustedDevices: false,
}

const MOCK_STATS = {
  totalUsers: 124,

  enrolledUsers: 109,

  pendingUsers: 15,

  compliance: '88%',
}

export function MFAModule() {
  const [settings, setSettings] = useState<MFASettings>(MOCK_MFA)

  function toggleEnforcement() {
    setSettings({
      ...settings,
      enforced: !settings.enforced,
    })
  }

  function toggleTrustedDevices() {
    setSettings({
      ...settings,
      trustedDevices: !settings.trustedDevices,
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}

      <div>
        <h1
          className="
          flex
          items-center
          gap-2
          text-xl
          font-bold
        "
        >
          <ShieldCheck className="h-5 w-5 text-primary" />
          Multi-Factor Authentication
        </h1>

        <p
          className="
          text-sm
          text-muted-foreground
        "
        >
          Manage tenant identity protection policies.
        </p>
      </div>

      {/* Status Cards */}

      <div
        className="
        grid
        gap-4
        md:grid-cols-4
      "
      >
        <Card>
          <CardContent className="p-4">
            <div
              className="
              flex
              items-center
              gap-3
            "
            >
              <Users className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Total Users</p>

                <p className="text-xl font-bold">{MOCK_STATS.totalUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div
              className="
              flex
              items-center
              gap-3
            "
            >
              <CheckCircle className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">MFA Enabled</p>

                <p className="text-xl font-bold">{MOCK_STATS.enrolledUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div
              className="
              flex
              items-center
              gap-3
            "
            >
              <AlertTriangle className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Pending Setup</p>

                <p className="text-xl font-bold">{MOCK_STATS.pendingUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div
              className="
              flex
              items-center
              gap-3
            "
            >
              <Lock className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Compliance</p>

                <p className="text-xl font-bold">{MOCK_STATS.compliance}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Policy Configuration */}

      <Card>
        <CardHeader>
          <CardTitle>MFA Policy</CardTitle>
        </CardHeader>

        <CardContent className="space-y-5">
          <div
            className="
            flex
            items-center
            justify-between
          "
          >
            <div>
              <p className="font-medium">Enforce MFA</p>

              <p
                className="
                text-sm
                text-muted-foreground
              "
              >
                Require all tenant users to configure MFA.
              </p>
            </div>

            <Button
              onClick={toggleEnforcement}
              variant={settings.enforced ? 'default' : 'outline'}
            >
              {settings.enforced ? 'Enabled' : 'Disabled'}
            </Button>
          </div>

          <div>
            <p
              className="
              mb-3
              font-medium
            "
            >
              Allowed Authentication Methods
            </p>

            <div
              className="
              flex
              flex-wrap
              gap-2
            "
            >
              {settings.methods.map((method) => (
                <Badge key={method} variant="outline">
                  {method}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Options */}

      <Card>
        <CardHeader>
          <CardTitle>Security Options</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <div
            className="
            flex
            justify-between
            items-center
          "
          >
            <div
              className="
              flex
              items-center
              gap-3
            "
            >
              <Smartphone className="h-5 w-5 text-primary" />

              <div>
                <p className="font-medium">Trusted Devices</p>

                <p
                  className="
                  text-sm
                  text-muted-foreground
                "
                >
                  Allow users to remember devices.
                </p>
              </div>
            </div>

            <Button
              variant={settings.trustedDevices ? 'default' : 'outline'}
              onClick={toggleTrustedDevices}
            >
              {settings.trustedDevices ? 'Enabled' : 'Disabled'}
            </Button>
          </div>

          <div
            className="
            flex
            items-center
            gap-3
          "
          >
            <KeyRound className="h-5 w-5 text-primary" />

            <div>
              <p className="font-medium">Recovery Codes</p>

              <Badge variant="outline">Enabled</Badge>
            </div>
          </div>

          <div
            className="
            flex
            items-center
            gap-3
          "
          >
            <Mail className="h-5 w-5 text-primary" />

            <div>
              <p className="font-medium">Email OTP</p>

              <Badge variant="outline">Allowed</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
