import { redirect } from 'next/navigation'
import Link from 'next/link'
import { ShieldHalf, LogOut } from 'lucide-react'

import { getCurrentUser } from '@/lib/api/auth'
import { AdminNav } from '@/components/admin/admin-nav'

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const user = await getCurrentUser()

  if (!user) {
    redirect('/login')
  }

  if (user.role !== 'admin') {
    redirect('/dashboard')
  }

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 flex w-64 flex-col border-r border-sidebar-border bg-sidebar">
        <div className="flex items-center gap-2.5 border-b border-sidebar-border px-5 py-4">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary">
            <ShieldHalf className="h-5 w-5" />
          </span>

          <div>
            <p className="font-bold">
              BLVCK<span className="text-primary">CYBER</span>
            </p>

            <p className="text-xs text-muted-foreground">Internal Operations</p>
          </div>
        </div>

        <AdminNav />

        <div className="border-t p-3">
          <div className="rounded bg-sidebar-accent/40 px-3 py-2 text-xs">
            {user.email}
          </div>

          <Link
            href="/logout"
            className="mt-3 flex items-center gap-2 rounded px-3 py-2 hover:bg-destructive/10"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Link>
        </div>
      </aside>

      <main className="flex-1 pl-64">{children}</main>
    </div>
  )
}
