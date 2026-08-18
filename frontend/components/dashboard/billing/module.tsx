'use client'

import {
  CreditCard,
  Download,
  Users,
  HardDrive,
  ShieldCheck,
  CalendarDays,
  Receipt,
  ArrowUpRight,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

import { Button } from '@/components/ui/button'

import { Badge } from '@/components/ui/badge'

type Invoice = {
  id: string
  date: string
  amount: string
  status: 'Paid' | 'Pending'
}

const MOCK_BILLING = {
  plan: 'Enterprise',

  status: 'Active',

  billingCycle: 'Monthly',

  nextBilling: '01 September 2026',

  users: {
    used: 124,
    limit: 500,
  },

  storage: {
    used: '420 GB',
    limit: '2 TB',
  },

  payment: {
    method: 'Visa ending 4242',
    expiry: '08/2028',
  },
}

const MOCK_INVOICES: Invoice[] = [
  {
    id: 'INV-2026-008',
    date: '01 August 2026',
    amount: '$499',
    status: 'Paid',
  },

  {
    id: 'INV-2026-007',
    date: '01 July 2026',
    amount: '$499',
    status: 'Paid',
  },

  {
    id: 'INV-2026-006',
    date: '01 June 2026',
    amount: '$499',
    status: 'Paid',
  },
]

export function BillingModule() {
  function upgradePlan() {
    console.log('Upgrade plan')
  }

  function downloadInvoice(invoice: Invoice) {
    console.log('Download invoice', invoice.id)
  }

  return (
    <div className="space-y-6">
      {/* Header */}

      <div
        className="
        flex
        items-center
        justify-between
      "
      >
        <div>
          <h1
            className="
            flex
            items-center
            gap-2
            text-xl
            font-bold
          "
          >
            <CreditCard className="h-5 w-5 text-primary" />
            Billing & Subscription
          </h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Manage your organization's subscription and billing details.
          </p>
        </div>

        <Button onClick={upgradePlan}>
          <ArrowUpRight className="mr-2 h-4 w-4" />
          Upgrade Plan
        </Button>
      </div>

      {/* Subscription */}

      <Card>
        <CardHeader>
          <CardTitle>Current Subscription</CardTitle>
        </CardHeader>

        <CardContent>
          <div
            className="
            flex
            items-center
            justify-between
          "
          >
            <div className="space-y-2">
              <div
                className="
                flex
                items-center
                gap-2
              "
              >
                <ShieldCheck className="h-5 w-5 text-primary" />

                <p
                  className="
                  text-lg
                  font-semibold
                "
                >
                  BLVCK CYBER {MOCK_BILLING.plan}
                </p>

                <Badge>{MOCK_BILLING.status}</Badge>
              </div>

              <p
                className="
                text-sm
                text-muted-foreground
              "
              >
                Billing cycle: {MOCK_BILLING.billingCycle}
              </p>

              <p
                className="
                text-sm
                text-muted-foreground
              "
              >
                Next billing date: {MOCK_BILLING.nextBilling}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage */}

      <div
        className="
        grid
        gap-4
        md:grid-cols-3
      "
      >
        <Card>
          <CardContent className="p-5">
            <div
              className="
              flex
              gap-3
              items-center
            "
            >
              <Users className="h-5 w-5 text-primary" />

              <div>
                <p
                  className="
                  text-xs
                  text-muted-foreground
                "
                >
                  Users
                </p>

                <p className="font-bold text-xl">
                  {MOCK_BILLING.users.used}

                  <span
                    className="
                    text-sm
                    text-muted-foreground
                  "
                  >
                    /{MOCK_BILLING.users.limit}
                  </span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div
              className="
              flex
              gap-3
              items-center
            "
            >
              <HardDrive className="h-5 w-5 text-primary" />

              <div>
                <p
                  className="
                  text-xs
                  text-muted-foreground
                "
                >
                  Storage
                </p>

                <p className="font-bold text-xl">{MOCK_BILLING.storage.used}</p>

                <p
                  className="
                  text-xs
                  text-muted-foreground
                "
                >
                  of {MOCK_BILLING.storage.limit}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div
              className="
              flex
              gap-3
              items-center
            "
            >
              <CalendarDays className="h-5 w-5 text-primary" />

              <div>
                <p
                  className="
                  text-xs
                  text-muted-foreground
                "
                >
                  Renewal
                </p>

                <p className="font-bold">Monthly</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Payment Method */}

      <Card>
        <CardHeader>
          <CardTitle>Payment Method</CardTitle>
        </CardHeader>

        <CardContent>
          <div
            className="
            flex
            items-center
            gap-3
          "
          >
            <CreditCard className="h-5 w-5 text-primary" />

            <div>
              <p className="font-medium">{MOCK_BILLING.payment.method}</p>

              <p
                className="
                text-sm
                text-muted-foreground
              "
              >
                Expires {MOCK_BILLING.payment.expiry}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Invoices */}

      <Card>
        <CardHeader>
          <CardTitle
            className="
            flex
            items-center
            gap-2
          "
          >
            <Receipt className="h-5 w-5" />
            Invoice History
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-3">
          {MOCK_INVOICES.map((invoice) => (
            <div
              key={invoice.id}
              className="
                flex
                items-center
                justify-between
                rounded-lg
                border
                p-4
              "
            >
              <div>
                <p className="font-medium">{invoice.id}</p>

                <p
                  className="
                  text-sm
                  text-muted-foreground
                "
                >
                  {invoice.date}
                </p>
              </div>

              <div
                className="
                flex
                items-center
                gap-4
              "
              >
                <Badge>{invoice.status}</Badge>

                <span className="font-medium">{invoice.amount}</span>

                <Button
                  size="icon"
                  variant="outline"
                  onClick={() => downloadInvoice(invoice)}
                >
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
