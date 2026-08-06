import { NextResponse } from 'next/server'

export async function GET() {
  const backend = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

  return NextResponse.redirect(new URL(`${backend}/auth/logout`))
}
