'use client'

import {
  Shield,
  Users,
  KeyRound,
  MoreHorizontal,
  Plus,
  Lock,
} from 'lucide-react'

const roles = [
  {
    id: 1,

    name: 'Tenant Administrator',

    key: 'ADMIN',

    description:
      'Full access to tenant security operations, users and configuration.',

    users: 2,

    permissions: 48,

    category: 'System',
  },

  {
    id: 2,

    name: 'SOC Analyst',

    key: 'SOC_ANALYST',

    description:
      'Monitor alerts, incidents and threat intelligence activities.',

    users: 8,

    permissions: 24,

    category: 'Security Operations',
  },

  {
    id: 3,

    name: 'Security Engineer',

    key: 'SECURITY_ENGINEER',

    description: 'Manage assets, vulnerabilities and security controls.',

    users: 5,

    permissions: 31,

    category: 'Engineering',
  },

  {
    id: 4,

    name: 'Viewer',

    key: 'VIEWER',

    description: 'Read-only access to dashboards and reports.',

    users: 15,

    permissions: 8,

    category: 'Basic',
  },
]

const permissionGroups = [
  {
    name: 'Users Management',
    permissions: ['users.view', 'users.create', 'users.update', 'users.delete'],
  },

  {
    name: 'Security Operations',
    permissions: ['alerts.view', 'incidents.view', 'threatintel.view'],
  },

  {
    name: 'Administration',
    permissions: ['roles.manage', 'settings.manage', 'billing.view'],
  },
]

export function RolesModule() {
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
            text-2xl
            font-bold
          "
          >
            Roles & Permissions
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Manage tenant roles and access control policies.
          </p>
        </div>

        <button
          className="
            flex
            items-center
            gap-2
            rounded-lg
            bg-primary
            px-4
            py-2
            text-sm
            font-semibold
            text-primary-foreground
          "
        >
          <Plus className="h-4 w-4" />
          Create Role
        </button>
      </div>

      {/* Roles */}

      <div
        className="
        grid
        gap-5
        md:grid-cols-2
      "
      >
        {roles.map((role) => (
          <div
            key={role.id}
            className="
              rounded-xl
              border
              bg-card
              p-5
            "
          >
            <div
              className="
              flex
              items-start
              justify-between
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
                  flex
                  h-10
                  w-10
                  items-center
                  justify-center
                  rounded-lg
                  bg-primary/10
                  text-primary
                "
                >
                  <Shield className="h-5 w-5" />
                </div>

                <div>
                  <h2
                    className="
                    font-semibold
                  "
                  >
                    {role.name}
                  </h2>

                  <p
                    className="
                    text-xs
                    text-muted-foreground
                  "
                  >
                    {role.key}
                  </p>
                </div>
              </div>

              <button>
                <MoreHorizontal
                  className="
                    h-5
                    w-5
                    text-muted-foreground
                  "
                />
              </button>
            </div>

            <p
              className="
              mt-4
              text-sm
              text-muted-foreground
            "
            >
              {role.description}
            </p>

            <div
              className="
              mt-5
              grid
              grid-cols-2
              gap-3
            "
            >
              <div
                className="
                rounded-lg
                bg-muted/50
                p-3
              "
              >
                <div
                  className="
                  flex
                  items-center
                  gap-2
                  text-xs
                  text-muted-foreground
                "
                >
                  <Users className="h-4 w-4" />
                  Users
                </div>

                <p
                  className="
                  mt-1
                  text-lg
                  font-bold
                "
                >
                  {role.users}
                </p>
              </div>

              <div
                className="
                rounded-lg
                bg-muted/50
                p-3
              "
              >
                <div
                  className="
                  flex
                  items-center
                  gap-2
                  text-xs
                  text-muted-foreground
                "
                >
                  <KeyRound className="h-4 w-4" />
                  Permissions
                </div>

                <p
                  className="
                  mt-1
                  text-lg
                  font-bold
                "
                >
                  {role.permissions}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Permission Matrix */}

      <div
        className="
        rounded-xl
        border
        bg-card
        p-6
      "
      >
        <div
          className="
          mb-5
          flex
          items-center
          gap-3
        "
        >
          <Lock
            className="
            h-5
            w-5
            text-primary
          "
          />

          <h2
            className="
            font-semibold
          "
          >
            Permission Groups
          </h2>
        </div>

        <div
          className="
          grid
          gap-4
          md:grid-cols-3
        "
        >
          {permissionGroups.map((group) => (
            <div
              key={group.name}
              className="
                rounded-lg
                border
                p-4
              "
            >
              <h3
                className="
                mb-3
                text-sm
                font-semibold
              "
              >
                {group.name}
              </h3>

              <div className="space-y-2">
                {group.permissions.map((permission) => (
                  <div
                    key={permission}
                    className="
                      rounded-md
                      bg-muted
                      px-3
                      py-2
                      text-xs
                      font-medium
                    "
                  >
                    {permission}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
