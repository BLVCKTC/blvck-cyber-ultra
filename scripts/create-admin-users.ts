import { config } from "dotenv"
config({ path: ".env.local" })

import { WorkOS } from "@workos-inc/node"

// One-off script — run this once per admin user, then delete or ignore.
// Uses your staging API key (sk_test_...) — never run this against
// a production key.

const workos = new WorkOS(process.env.WORKOS_API_KEY!)

const ADMIN_USERS = [
  {
    email: "admin@blvckcyber.com",
    password: "root123blvck",
    firstName: "Admin",
    lastName: "Blvck",
  },
  {
    email: "support@blvckcyber.com",
    password: "root123blvck",
    firstName: "Support",
    lastName: "Blvck",
  },
]

async function createAdminUsers() {
  for (const u of ADMIN_USERS) {
    try {
      const user = await workos.userManagement.createUser({
        email: u.email,
        password: u.password,
        firstName: u.firstName,
        lastName: u.lastName,
        emailVerified: true,
      })
      console.log(`Created: ${user.email} (id: ${user.id})`)
    } catch (err) {
      console.error(`Failed to create ${u.email}:`, err instanceof Error ? err.message : err)
    }
  }
}

createAdminUsers()