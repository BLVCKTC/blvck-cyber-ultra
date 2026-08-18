"use client"

import { LogOut } from "lucide-react"

type SidebarUserProps = {
  user?: {
    firstName?: string | null
    lastName?: string | null
    email?: string | null
  } | null
}

export function SidebarUser({
  user,
}: SidebarUserProps) {

  const name =
    [user?.firstName, user?.lastName]
      .filter(
        (part): part is string =>
          Boolean(part)
      )
      .join(" ") || "Authenticated User"

  const initials =
    name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U"

  const handleLogout = () => {
    // 1. Clear any local browser state
    localStorage.removeItem("user_session");
    
    // 2. Perform a full page redirect directly to your WorkOS /logout route handler
    window.location.href = "/logout";
  };

  return (
    <div className="flex flex-col gap-2 rounded-md bg-sidebar-accent/40 p-3 border border-border/40">
      {/* User Information Panel */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyan-500/10 border border-cyan-500/30 font-mono text-xs font-bold text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.15)]">
          {initials}
        </div>

        <div className="min-w-0 leading-tight flex-1">
          <p className="truncate text-xs font-medium text-foreground">
            {name}
          </p>
          <p className="truncate font-mono text-[10px] text-muted-foreground/80">
            {user?.email ?? "secure_node@mainframe"}
          </p>
        </div>
      </div>

      {/* Cyber-themed Logout Action Button */}
      <button
        onClick={handleLogout}
        className="mt-1 flex w-full items-center justify-between rounded bg-red-950/20 px-2.5 py-1.5 font-mono text-[10px] font-medium text-red-400 border border-red-900/30 transition-all hover:bg-red-950/40 hover:text-red-300 hover:border-red-500/50"
      >
        <span>SYS_DISCONNECT</span>
        <LogOut className="h-3 w-3 text-red-400/80" />
      </button>
    </div>
  )
}
