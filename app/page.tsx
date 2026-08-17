import { redirect } from 'next/navigation'

// The authentication experience begins at /login.
export default function RootPage() {
  redirect('/login')
}
