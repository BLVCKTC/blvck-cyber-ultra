'use client'

import { useState } from 'react'

import {
  Activity,
  Download,
  Eye,
  ShieldAlert,
  User,
  Globe,
  Clock,
  FileSearch,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

import { Button } from '@/components/ui/button'

import { Badge } from '@/components/ui/badge'

type AuditEvent = {
  id: number
  actor: string
  email: string
  action: string
  target: string
  category: string
  severity: 'Low' | 'Medium' | 'High' | 'Critical'
  ip: string
  timestamp: string
}

const MOCK_AUDIT_EVENTS: AuditEvent[] = [
  {
    id: 1,
    actor: 'System Administrator',
    email: 'admin@blvckcyber.com',
    action: 'Updated MFA Policy',
    target: 'Tenant Security Settings',
    category: 'Identity',
    severity: 'High',
    ip: '192.168.1.25',
    timestamp: '2026-08-06 14:32',
  },

  {
    id: 2,
    actor: 'Security Analyst',
    email: 'analyst@blvckcyber.com',
    action: 'Closed Security Alert',
    target: 'Incident #INC-2048',
    category: 'Incident Response',
    severity: 'Medium',
    ip: '41.79.xxx.xxx',
    timestamp: '2026-08-06 13:15',
  },

  {
    id: 3,
    actor: 'API Integration',
    email: 'siem@blvckcyber.com',
    action: 'Generated API Key',
    target: 'SOC Connector',
    category: 'API Management',
    severity: 'Low',
    ip: '10.0.0.50',
    timestamp: '2026-08-06 11:05',
  },

  {
    id: 4,
    actor: 'Unknown User',
    email: 'unknown',
    action: 'Failed Login Attempt',
    target: 'Admin Account',
    category: 'Authentication',
    severity: 'Critical',
    ip: '185.xxx.xxx.xxx',
    timestamp: '2026-08-06 09:44',
  },
]

export function AuditModule() {
  const [events] = useState<AuditEvent[]>(MOCK_AUDIT_EVENTS)

  function exportLogs() {
    console.log('Export audit logs')
  }

  function viewEvent(event: AuditEvent) {
    console.log(event)
  }

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
            <Activity className="h-5 w-5 text-primary" />
            Audit Logs
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Track all tenant security and administrative activities.
          </p>
        </div>

        <Button onClick={exportLogs}>
          <Download className="mr-2 h-4 w-4" />
          Export
        </Button>
      </div>

      {/* Summary */}

      <div
        className="
        grid
        gap-4
        md:grid-cols-4
      "
      >
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Events Today</p>

            <p className="text-2xl font-bold">248</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Critical Events</p>

            <p className="text-2xl font-bold">3</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Users Tracked</p>

            <p className="text-2xl font-bold">124</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Compliance Status</p>

            <Badge className="mt-2">Healthy</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}

      <Card>
        <CardHeader>
          <CardTitle>Security Activity Timeline</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          {events.map((event) => (
            <div
              key={event.id}
              className="
                rounded-lg
                border
                p-4
                space-y-3
              "
            >
              <div
                className="
                flex
                justify-between
                items-start
              "
              >
                <div
                  className="
                  flex
                  gap-3
                "
                >
                  <div
                    className="
                    rounded-full
                    bg-primary/10
                    p-2
                  "
                  >
                    <FileSearch className="h-4 w-4 text-primary" />
                  </div>

                  <div>
                    <p
                      className="
                      font-medium
                    "
                    >
                      {event.action}
                    </p>

                    <p
                      className="
                      text-sm
                      text-muted-foreground
                    "
                    >
                      {event.target}
                    </p>
                  </div>
                </div>

                <Badge
                  variant={
                    event.severity === 'Critical' ? 'destructive' : 'outline'
                  }
                >
                  {event.severity}
                </Badge>
              </div>

              <div
                className="
                grid
                gap-3
                text-sm
                md:grid-cols-5
              "
              >
                <div>
                  <p className="text-muted-foreground">Actor</p>

                  <p className="flex gap-1 items-center">
                    <User className="h-3 w-3" />

                    {event.actor}
                  </p>
                </div>

                <div>
                  <p className="text-muted-foreground">Category</p>

                  <p>{event.category}</p>
                </div>

                <div>
                  <p className="text-muted-foreground">IP Address</p>

                  <p className="flex gap-1 items-center">
                    <Globe className="h-3 w-3" />

                    {event.ip}
                  </p>
                </div>

                <div>
                  <p className="text-muted-foreground">Time</p>

                  <p className="flex gap-1 items-center">
                    <Clock className="h-3 w-3" />

                    {event.timestamp}
                  </p>
                </div>

                <div className="flex items-end">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => viewEvent(event)}
                  >
                    <Eye className="mr-2 h-4 w-4" />
                    View
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
