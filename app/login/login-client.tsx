"use client"

import Link from "next/link"
import { ShieldCheck, KeyRound, Building2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { AuthShell } from "@/components/auth/auth-shell"
import { getLoginUrl } from "@/lib/auth/keycloak"

const TRUST_POINTS = [
  {
    icon: ShieldCheck,
    label: "Multi-factor authentication",
  },
  {
    icon: KeyRound,
    label: "Authorization Code + PKCE",
  },
  {
    icon: Building2,
    label: "Enterprise tenant security",
  },
]

export function LoginClient() {
function signIn() {

  window.location.href =
    getLoginUrl("BLVCK-CYBER")

}

  return (
    <AuthShell
      title="Security Operations Access"
      subtitle="Sign in securely using your organization account."
    >
      <Button
        type="button"
        className="w-full glow"
        size="lg"
        onClick={signIn}
      >
        Continue to Secure Sign In
      </Button>

      <div className="mt-6 space-y-2">
        {TRUST_POINTS.map((item) => (
          <div
            key={item.label}
            className="flex items-center gap-2 text-xs text-muted-foreground"
          >
            <item.icon className="h-3.5 w-3.5 text-primary" />
            {item.label}
          </div>
        ))}
      </div>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        New organization?{" "}
        <Link
          href="/signup"
          className="text-primary hover:underline"
        >
          Contact BLVCK CYBER
        </Link>
      </p>
    </AuthShell>
  )
}