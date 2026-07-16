import { FileBarChart, Download, ShieldCheck, FileText, Gauge, Sparkles } from "lucide-react"
import { Panel } from "./panel"

const reports = [
  { title: "Executive Security Summary", desc: "Board-ready posture overview", icon: Gauge, updated: "Today" },
  { title: "Vulnerability Assessment", desc: "Full CVE + remediation report", icon: ShieldCheck, updated: "Today" },
  { title: "Compliance Report", desc: "PCI-DSS, GDPR, NDPR status", icon: FileText, updated: "Yesterday" },
  { title: "AI Threat Insights", desc: "ML-driven forecast & anomalies", icon: Sparkles, updated: "2 days ago" },
]

export function ReportsPanel() {
  return (
    <Panel title="Reports & Insights" icon={<FileBarChart className="h-4 w-4" />}>
      <div className="grid gap-3 sm:grid-cols-2">
        {reports.map((r) => {
          const Icon = r.icon
          return (
            <div
              key={r.title}
              className="group flex items-center gap-3 rounded-md border border-border bg-background/40 p-3 transition-colors hover:border-primary/40"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-foreground">{r.title}</p>
                <p className="truncate font-mono text-[10px] text-muted-foreground">
                  {r.desc} · {r.updated}
                </p>
              </div>
              <button
                className="rounded border border-border p-1.5 text-muted-foreground transition-colors group-hover:border-primary/40 group-hover:text-primary"
                aria-label={`Download ${r.title}`}
              >
                <Download className="h-4 w-4" />
              </button>
            </div>
          )
        })}
      </div>
    </Panel>
  )
}
