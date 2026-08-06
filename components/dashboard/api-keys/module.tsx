'use client'

import { useState } from 'react'
import { Copy, KeyRound, Plus, ShieldCheck, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

type ApiKey = {
  id: number
  name: string
  key: string
  createdBy: string
  createdAt: string
  lastUsed: string
  status: 'Active' | 'Revoked'
  permissions: string[]
}

const MOCK_API_KEYS: ApiKey[] = [
  {
    id: 1,
    name: 'SOC Integration',
    key: 'blvck_live_82hsh72js92ks',
    createdBy: 'System Administrator',
    createdAt: '2026-08-01',
    lastUsed: '2 hours ago',
    status: 'Active',
    permissions: ['alerts.view', 'incidents.view', 'assets.view'],
  },

  {
    id: 2,
    name: 'SIEM Connector',
    key: 'blvck_live_92jsk82js82js',
    createdBy: 'Security Admin',
    createdAt: '2026-07-20',
    lastUsed: 'Yesterday',
    status: 'Active',
    permissions: ['logs.read', 'events.read'],
  },

  {
    id: 3,
    name: 'Old Scanner',
    key: 'blvck_live_xxx82382',
    createdBy: 'Admin',
    createdAt: '2026-06-11',
    lastUsed: 'Never',
    status: 'Revoked',
    permissions: ['vulnerabilities.view'],
  },
]

export function ApiKeysModule() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>(MOCK_API_KEYS)

  function createKey() {
    const newKey: ApiKey = {
      id: Date.now(),
      name: 'New API Key',
      key: `blvck_live_${Date.now()}`,
      createdBy: 'Current User',
      createdAt: new Date().toISOString().split('T')[0],
      lastUsed: 'Never',
      status: 'Active',
      permissions: ['dashboard.view'],
    }

    setApiKeys([...apiKeys, newKey])
  }

  function revokeKey(id: number) {
    setApiKeys(
      apiKeys.map((key) =>
        key.id === id
          ? {
              ...key,
              status: 'Revoked',
            }
          : key,
      ),
    )
  }

  function copyKey(value: string) {
    navigator.clipboard.writeText(value)
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
            text-xl
            font-bold
            flex
            items-center
            gap-2
          "
          >
            <KeyRound className="h-5 w-5 text-primary" />
            API Keys
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Manage tenant API access and integrations.
          </p>
        </div>

        <Button onClick={createKey}>
          <Plus className="mr-2 h-4 w-4" />
          Create Key
        </Button>
      </div>

      {/* API Keys */}

      <div className="grid gap-4">
        {apiKeys.map((api) => (
          <Card key={api.id}>
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
                  <ShieldCheck className="h-4 w-4 text-primary" />

                  {api.name}
                </CardTitle>

                <Badge
                  variant={api.status === 'Active' ? 'default' : 'destructive'}
                >
                  {api.status}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div
                className="
                rounded-lg
                bg-muted
                p-3
                flex
                justify-between
                items-center
              "
              >
                <code
                  className="
                  text-xs
                  truncate
                "
                >
                  {api.key}
                </code>

                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => copyKey(api.key)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>

              <div
                className="
                grid
                md:grid-cols-3
                gap-4
                text-sm
              "
              >
                <div>
                  <p className="text-muted-foreground">Created By</p>

                  <p className="font-medium">{api.createdBy}</p>
                </div>

                <div>
                  <p className="text-muted-foreground">Created</p>

                  <p className="font-medium">{api.createdAt}</p>
                </div>

                <div>
                  <p className="text-muted-foreground">Last Used</p>

                  <p className="font-medium">{api.lastUsed}</p>
                </div>
              </div>

              <div>
                <p
                  className="
                  text-xs
                  text-muted-foreground
                  mb-2
                "
                >
                  Permissions
                </p>

                <div className="flex flex-wrap gap-2">
                  {api.permissions.map((permission) => (
                    <Badge key={permission} variant="outline">
                      {permission}
                    </Badge>
                  ))}
                </div>
              </div>

              {api.status === 'Active' && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => revokeKey(api.id)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Revoke Key
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
