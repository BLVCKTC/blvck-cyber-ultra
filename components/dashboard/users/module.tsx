'use client'

import {
  UserPlus,
  Search,
  ShieldCheck,
  Mail,
  Clock,
  MoreHorizontal,
  UserCircle,
} from 'lucide-react'

import { useState } from 'react'

const users = [
  {
    id: 1,
    name: 'System Administrator',
    email: 'admin@blvckcyber.com',
    role: 'ADMIN',
    status: 'Active',
    mfa: true,
    lastLogin: '5 minutes ago',
  },

  {
    id: 2,
    name: 'Tendai Moyo',
    email: 'tendai@blvckcyber.com',
    role: 'SOC ANALYST',
    status: 'Active',
    mfa: true,
    lastLogin: '1 hour ago',
  },

  {
    id: 3,
    name: 'Sarah Dube',
    email: 'sarah@blvckcyber.com',
    role: 'SECURITY ENGINEER',
    status: 'Active',
    mfa: false,
    lastLogin: 'Yesterday',
  },

  {
    id: 4,
    name: 'John Ncube',
    email: 'john@blvckcyber.com',
    role: 'VIEWER',
    status: 'Inactive',
    mfa: false,
    lastLogin: '30 days ago',
  },
]

export function UsersModule() {
  const [search, setSearch] = useState('')

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(search.toLowerCase()) ||
      user.email.toLowerCase().includes(search.toLowerCase()),
  )

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
            Users
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Manage users and tenant access permissions.
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
          <UserPlus className="h-4 w-4" />
          Invite User
        </button>
      </div>

      {/* Search */}

      <div
        className="
        flex
        items-center
        gap-3
        rounded-xl
        border
        bg-card
        px-4
        py-3
      "
      >
        <Search
          className="
          h-4
          w-4
          text-muted-foreground
        "
        />

        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search users..."
          className="
            flex-1
            bg-transparent
            text-sm
            outline-none
          "
        />
      </div>

      {/* Users Table */}

      <div
        className="
        overflow-hidden
        rounded-xl
        border
        bg-card
      "
      >
        <table
          className="
          w-full
          text-sm
        "
        >
          <thead>
            <tr
              className="
              border-b
              text-left
              text-xs
              uppercase
              text-muted-foreground
            "
            >
              <th className="px-5 py-4">User</th>

              <th className="px-5 py-4">Role</th>

              <th className="px-5 py-4">MFA</th>

              <th className="px-5 py-4">Status</th>

              <th className="px-5 py-4">Last Login</th>

              <th />
            </tr>
          </thead>

          <tbody>
            {filteredUsers.map((user) => (
              <tr
                key={user.id}
                className="
                border-b
                last:border-none
                hover:bg-muted/40
              "
              >
                <td
                  className="
                px-5
                py-4
              "
                >
                  <div
                    className="
                  flex
                  items-center
                  gap-3
                "
                  >
                    <div
                      className="
                    flex
                    h-9
                    w-9
                    items-center
                    justify-center
                    rounded-full
                    bg-primary/10
                    text-primary
                  "
                    >
                      <UserCircle className="h-5 w-5" />
                    </div>

                    <div>
                      <p className="font-medium">{user.name}</p>

                      <p
                        className="
                      flex
                      items-center
                      gap-1
                      text-xs
                      text-muted-foreground
                    "
                      >
                        <Mail className="h-3 w-3" />

                        {user.email}
                      </p>
                    </div>
                  </div>
                </td>

                <td className="px-5 py-4">
                  <span
                    className="
                  rounded-md
                  bg-primary/10
                  px-2
                  py-1
                  text-xs
                  font-semibold
                  text-primary
                "
                  >
                    {user.role}
                  </span>
                </td>

                <td className="px-5 py-4">
                  {user.mfa ? (
                    <span
                      className="
                    flex
                    items-center
                    gap-1
                    text-green-500
                  "
                    >
                      <ShieldCheck className="h-4 w-4" />
                      Enabled
                    </span>
                  ) : (
                    <span
                      className="
                    text-muted-foreground
                  "
                    >
                      Disabled
                    </span>
                  )}
                </td>

                <td className="px-5 py-4">
                  <span
                    className="
                  rounded-md
                  bg-muted
                  px-2
                  py-1
                  text-xs
                "
                  >
                    {user.status}
                  </span>
                </td>

                <td
                  className="
                px-5
                py-4
                text-muted-foreground
              "
                >
                  <div
                    className="
                  flex
                  items-center
                  gap-2
                "
                  >
                    <Clock className="h-4 w-4" />

                    {user.lastLogin}
                  </div>
                </td>

                <td className="px-5 py-4">
                  <button>
                    <MoreHorizontal className="h-5 w-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
