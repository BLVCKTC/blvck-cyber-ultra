import { config } from "dotenv"
config({ path: ".env.local" })

import { WorkOS } from "@workos-inc/node"

const workos = new WorkOS(process.env.WORKOS_API_KEY!)

async function check() {

  const user = await workos.userManagement.getUser(
    "user_01KY70SDVMG4XME2NFNE2ENAXK"
  )

  console.log(user)

}

check()