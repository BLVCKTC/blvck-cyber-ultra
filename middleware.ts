import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const cookies = request.cookies.getAll()

  console.log('MIDDLEWARE COOKIES:', cookies)

  const token = request.cookies.get('session_kc_access')

  console.log('SESSION TOKEN:', token)

  const protectedRoutes = ['/dashboard', '/admin', '/app']

  const isProtected = protectedRoutes.some((route) =>
    request.nextUrl.pathname.startsWith(route),
  )

  if (isProtected && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*', '/app/:path*'],
}
