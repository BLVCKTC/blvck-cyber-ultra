'use client'

import {
  Users,
  UserPlus,
  Shield,
  Activity,
  MoreHorizontal,
  UserCircle,
} from 'lucide-react'

const teams = [
  {
    id: 1,
    name: 'Security Operations Center',
    description: 'Responsible for monitoring threats, alerts and incidents.',

    lead: 'System Administrator',

    members: 8,

    function: 'SOC',

    status: 'Active',
  },

  {
    id: 2,
    name: 'Incident Response Team',

    description: 'Handles security incidents and investigations.',

    lead: 'Tendai Moyo',

    members: 5,

    function: 'Incident Response',

    status: 'Active',
  },

  {
    id: 3,
    name: 'Threat Intelligence',

    description: 'Analyses threat feeds and intelligence reports.',

    lead: 'Sarah Dube',

    members: 4,

    function: 'Threat Intel',

    status: 'Active',
  },

  {
    id: 4,
    name: 'Security Auditors',

    description: 'Compliance reviews and security assessments.',

    lead: 'John Ncube',

    members: 3,

    function: 'Compliance',

    status: 'Inactive',
  },
]

export function TeamsModule() {
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
            Teams
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Manage security teams and operational groups.
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
          Create Team
        </button>
      </div>

      {/* Team Cards */}

      <div
        className="
          grid
          gap-5
          md:grid-cols-2
          xl:grid-cols-3
        "
      >
        {teams.map((team) => (
          <div
            key={team.id}
            className="
              rounded-xl
              border
              bg-card
              p-5
              transition
              hover:border-primary/40
            "
          >
            {/* Title */}

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
                    {team.name}
                  </h2>

                  <span
                    className="
                      text-xs
                      text-muted-foreground
                    "
                  >
                    {team.function}
                  </span>
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
              {team.description}
            </p>

            {/* Details */}

            <div
              className="
                mt-5
                space-y-3
                border-t
                pt-4
              "
            >
              <div
                className="
                  flex
                  items-center
                  justify-between
                "
              >
                <span
                  className="
                    text-xs
                    text-muted-foreground
                  "
                >
                  Team Lead
                </span>

                <span
                  className="
                    flex
                    items-center
                    gap-2
                    text-sm
                    font-medium
                  "
                >
                  <UserCircle
                    className="
                      h-4
                      w-4
                    "
                  />

                  {team.lead}
                </span>
              </div>

              <div
                className="
                  flex
                  items-center
                  justify-between
                "
              >
                <span
                  className="
                    text-xs
                    text-muted-foreground
                  "
                >
                  Members
                </span>

                <span
                  className="
                    flex
                    items-center
                    gap-2
                    text-sm
                  "
                >
                  <Users className="h-4 w-4" />

                  {team.members}
                </span>
              </div>

              <div
                className="
                  flex
                  items-center
                  justify-between
                "
              >
                <span
                  className="
                    text-xs
                    text-muted-foreground
                  "
                >
                  Status
                </span>

                <span
                  className="
                    flex
                    items-center
                    gap-1
                    rounded-md
                    bg-primary/10
                    px-2
                    py-1
                    text-xs
                    font-semibold
                    text-primary
                  "
                >
                  <Activity className="h-3 w-3" />

                  {team.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
