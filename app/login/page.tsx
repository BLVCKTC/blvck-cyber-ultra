import type { Metadata } from "next"
import { LoginClient } from "./login-client"

export const metadata: Metadata = {
  title: "Sign in — BLVCK CYBER",
}

export default function LoginPage() {
  return <LoginClient />
}
