'use client'

import { useState } from 'react'

import {
  Monitor,
  Smartphone,
  Globe,
  ShieldCheck,
  LogOut,
  AlertTriangle,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

import { Button } from '@/components/ui/button'

import { Badge } from '@/components/ui/badge'

type Session = {
  id: number
  user: string
  email: string
  device: string
  browser: string
  ip: string
  location: string
  lastActive: string
  status: 'Active' | 'Expired'
  current?: boolean
}

const MOCK_SESSIONS: Session[] = [
  {
    id: 1,
    user: 'System Administrator',
    email: 'admin@blvckcyber.com',
    device: 'Windows Desktop',
    browser: 'Chrome',
    ip: '192.168.1.25',
    location: 'Bulawayo, Zimbabwe',
    lastActive: 'Now',
    status: 'Active',
    current: true,
  },

  {
    id: 2,
    user: 'Security Analyst',
    email: 'analyst@blvckcyber.com',
    device: 'MacBook Pro',
    browser: 'Safari',
    ip: '41.79.xxx.xxx',
    location: 'Harare, Zimbabwe',
    lastActive: '10 minutes ago',
    status: 'Active',
  },

  {
    id: 3,
    user: 'SOC Engineer',
    email: 'soc@blvckcyber.com',
    device: 'Android Device',
    browser: 'Chrome Mobile',
    ip: '102.xxx.xxx.xxx',
    location: 'Cape Town, South Africa',
    lastActive: '2 days ago',
    status: 'Expired',
  },
]

export function SessionsModule() {
  const [sessions, setSessions] = useState<Session[]>(MOCK_SESSIONS)

  function revokeSession(id: number) {
    setSessions(
      sessions.map((session) =>
        session.id === id
          ? {
              ...session,
              status: 'Expired',
            }
          : session,
      ),
    )
  }

  function revokeAll() {
    setSessions(
      sessions.map((session) => ({
        ...session,
        status: 'Expired',
      })),
    )
  }

  const activeSessions = sessions.filter(
    (session) => session.status === 'Active',
  ).length

  return (
    <div className="space-y-6">
      {/* Header */}

      <div
        className="
        flex
        items-center
        justify-between
      "
      >
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
            Active Sessions
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Monitor and control tenant user sessions.
          </p>
        </div>

        <Button variant="destructive" onClick={revokeAll}>
          <LogOut className="mr-2 h-4 w-4" />
          Revoke All
        </Button>
      </div>

      {/* Statistics */}

      <div
        className="
        grid
        gap-4
        md:grid-cols-3
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
              <Monitor className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Active Sessions</p>

                <p className="text-xl font-bold">{activeSessions}</p>
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
              <Globe className="h-5 w-5 text-primary" />

              <div>
                <p className="text-xs text-muted-foreground">Locations</p>

                <p className="text-xl font-bold">3</p>
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
                <p className="text-xs text-muted-foreground">
                  Suspicious Sessions
                </p>

                <p className="text-xl font-bold">0</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Session List */}

      <div className="space-y-4">
        {sessions.map((session) => (
          <Card key={session.id}>
            <CardHeader>
              <div
                className="
                flex
                justify-between
                items-center
              "
              >
                <CardTitle
                  className="
                  flex
                  items-center
                  gap-2
                  text-base
                "
                >
                  {session.device.includes('Android') ? (
                    <Smartphone className="h-4 w-4" />
                  ) : (
                    <Monitor className="h-4 w-4" />
                  )}

                  {session.user}
                </CardTitle>

                <Badge
                  variant={
                    session.status === 'Active' ? 'default' : 'secondary'
                  }
                >
                  {session.current ? 'Current Session' : session.status}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div
                className="
                grid
                gap-4
                md:grid-cols-4
                text-sm
              "
              >
                <div>
                  <p className="text-muted-foreground">Email</p>

                  <p>{session.email}</p>
                </div>

                <div>
                  <p className="text-muted-foreground">Browser</p>

                  <p>{session.browser}</p>
                </div>

                <div>
                  <p className="text-muted-foreground">IP Address</p>

                  <p>{session.ip}</p>
                </div>

                <div>
                  <p className="text-muted-foreground">Location</p>

                  <p>{session.location}</p>
                </div>
              </div>

              <div
                className="
                flex
                justify-between
                items-center
              "
              >
                <p
                  className="
                  text-sm
                  text-muted-foreground
                "
                >
                  Last activity: {session.lastActive}
                </p>

                {!session.current && session.status === 'Active' && (
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => revokeSession(session.id)}
                  >
                    Revoke
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
