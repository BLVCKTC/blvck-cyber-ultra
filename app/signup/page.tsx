import type { Metadata } from 'next'
import { SignupClient } from './signup-client'

export const metadata: Metadata = {
  title: 'Create your account — BLVCK CYBER',
}

export default function SignupPage() {
  return <SignupClient />
}
