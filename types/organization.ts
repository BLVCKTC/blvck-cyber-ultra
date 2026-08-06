export type Organization = {
  id: string
  name: string
  legalName: string

  industry: string
  companySize: string

  country: string
  timezone: string

  website: string
  supportEmail: string
  supportPhone: string

  description: string

  logoUrl?: string

  security: {
    enforceMfa: boolean
    passwordExpiryDays: number
    sessionTimeout: number
    idleTimeout: number
    ipRestrictions: boolean
    deviceTrust: boolean
  }

  branding: {
    primaryColor: string
    secondaryColor: string
    accentColor: string
    darkTheme: boolean
  }

  domains: {
    id: number
    domain: string
    verified: boolean
  }[]

  locations: {
    id: number
    name: string
    country: string
    city: string
    timezone: string
  }[]

  subscription: {
    plan: string
    users: number
    activeUsers: number
    storage: string
    renewalDate: string
  }
}
