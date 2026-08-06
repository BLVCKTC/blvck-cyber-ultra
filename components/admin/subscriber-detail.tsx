"use client"

import {
  Building2,
  Mail,
  User,
  MapPin,
  Calendar,
  ShieldCheck,
  CircleUser,
} from "lucide-react"
import {
  STATUS_LABEL,
  formatCurrency,
  formatDate,
  type Subscriber,
} from "@/lib/subscribers"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"

function DetailRow({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Mail
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <div className="min-w-0">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
        <div className="truncate text-sm text-foreground">{value}</div>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-3">
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-1 font-display text-lg font-bold text-foreground">{value}</div>
    </div>
  )
}

export function SubscriberDetail({
  subscriber,
  open,
  onOpenChange,
}: {
  subscriber: Subscriber | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-md">
        {subscriber ? (
          <>
            <SheetHeader className="space-y-0 text-left">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary">
                  {subscriber.tier}
                </Badge>
                <Badge variant="outline" className="border-border text-muted-foreground">
                  {STATUS_LABEL[subscriber.status]}
                </Badge>
              </div>
              <SheetTitle className="mt-3 font-display text-xl">{subscriber.company}</SheetTitle>
              <SheetDescription>
                Account {subscriber.id} · Managed by {subscriber.accountManager}
              </SheetDescription>
            </SheetHeader>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <Metric label="MRR" value={formatCurrency(subscriber.mrr)} />
              <Metric label="Health score" value={`${subscriber.healthScore}/100`} />
              <Metric label="Seats" value={subscriber.seats.toLocaleString()} />
              <Metric
                label="Endpoints"
                value={subscriber.endpointsProtected.toLocaleString()}
              />
            </div>

            <div className="mt-4 flex items-center gap-3 rounded-lg border border-primary/20 bg-primary/5 p-3">
              <ShieldCheck className="size-5 shrink-0 text-primary" />
              <div className="text-sm text-foreground">
                {subscriber.openIncidents === 0 ? (
                  <span>No open incidents. Environment is secure.</span>
                ) : (
                  <span>
                    <span className="font-semibold text-primary">
                      {subscriber.openIncidents}
                    </span>{" "}
                    open incident{subscriber.openIncidents > 1 ? "s" : ""} under SOC review.
                  </span>
                )}
              </div>
            </div>

            <Separator className="my-6" />

            <div className="space-y-4">
              <DetailRow icon={User} label="Primary contact" value={subscriber.contactName} />
              <DetailRow icon={Mail} label="Email" value={subscriber.email} />
              <DetailRow icon={MapPin} label="Region" value={subscriber.region} />
              <DetailRow icon={CircleUser} label="Account manager" value={subscriber.accountManager} />
              <DetailRow icon={Calendar} label="Customer since" value={formatDate(subscriber.joinedAt)} />
              <DetailRow icon={Building2} label="Next renewal" value={formatDate(subscriber.renewalAt)} />
            </div>

            <Separator className="my-6" />

            <div className="flex flex-col gap-2">
              <Button className="w-full">Open account workspace</Button>
              <Button variant="outline" className="w-full">
                Contact {subscriber.contactName.split(" ")[0]}
              </Button>
            </div>
          </>
        ) : null}
      </SheetContent>
    </Sheet>
  )
}
