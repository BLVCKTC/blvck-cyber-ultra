import { config } from "dotenv"
config({ path: ".env.local" })

import { WorkOS } from "@workos-inc/node"

const workos = new WorkOS(process.env.WORKOS_API_KEY!)

async function updateUsers() {
  await workos.userManagement.updateUser({
    userId: "user_01KY70SDVMG4XME2NFNE2ENAXK",
    metadata: {
      role: "admin",
    },
  })

  await workos.userManagement.updateUser({
    userId: "user_01KY70SEDYFMZH1N71CMBANCJN",
    metadata: {
      role: "staff",
    },
  })

  console.log("✅ User roles updated successfully.")
}

updateUsers().catch((err) => {
  console.error(err)
  process.exit(1)
})