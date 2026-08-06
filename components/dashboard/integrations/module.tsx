"use client";

import { useMemo, useState } from "react";
import { Plug, KeyRound, Webhook, BookOpen, CheckCircle2, XCircle, Circle, Search, Copy } from "lucide-react";
import { StatCard } from "@/components/shell/stat-card";
import { toast } from "sonner";

export const metadata = {
  title: "Integrations Marketplace — BLVCK CYBER",
  description:
    "Connect Microsoft 365, Google Workspace, AWS, Azure, GCP, EDR, SIEM, ITSM and ChatOps to BLVCK CYBER.",
};

type Cat = "Cloud" | "Identity" | "Endpoint" | "SIEM" | "ITSM" | "ChatOps";
type Status = "connected" | "available" | "error";
const INTEGRATIONS: { name: string; cat: Cat; status: Status; desc: string }[] = [
  { name: "Microsoft 365", cat: "Cloud", status: "connected", desc: "Mailflow, Defender for O365, DLP signals." },
  { name: "Google Workspace", cat: "Cloud", status: "connected", desc: "Gmail security, Drive audit, admin logs." },
  { name: "AWS", cat: "Cloud", status: "connected", desc: "CloudTrail, GuardDuty, Security Hub, WAF." },
  { name: "Microsoft Azure", cat: "Cloud", status: "available", desc: "Sentinel, Defender for Cloud, AAD signals." },
  { name: "Google Cloud (GCP)", cat: "Cloud", status: "error", desc: "SCC, Cloud Audit, Chronicle." },
  { name: "Kubernetes", cat: "Cloud", status: "connected", desc: "Falco runtime, audit logs, admission control." },
  { name: "Docker", cat: "Cloud", status: "available", desc: "Image scanning and runtime posture." },
  { name: "Active Directory", cat: "Identity", status: "connected", desc: "Authentications, group changes, GPO drift." },
  { name: "LDAP", cat: "Identity", status: "available", desc: "Generic directory sync." },
  { name: "Microsoft Defender XDR", cat: "Endpoint", status: "connected", desc: "Endpoint alerts, live response, isolation." },
  { name: "CrowdStrike Falcon", cat: "Endpoint", status: "connected", desc: "Detections, RTR, contain host." },
  { name: "SentinelOne", cat: "Endpoint", status: "available", desc: "Deep visibility, network quarantine." },
  { name: "Splunk", cat: "SIEM", status: "connected", desc: "Bidirectional index and dashboards." },
  { name: "Elastic Security", cat: "SIEM", status: "available", desc: "Detections engine, timelines." },
  { name: "Wazuh", cat: "SIEM", status: "available", desc: "OSSEC agents, FIM, log analysis." },
  { name: "ServiceNow", cat: "ITSM", status: "connected", desc: "Auto-create SecOps incidents & tasks." },
  { name: "Jira", cat: "ITSM", status: "available", desc: "Tickets, sprints, vulnerability tracking." },
  { name: "Slack", cat: "ChatOps", status: "connected", desc: "Alerts, approvals, war rooms." },
  { name: "Microsoft Teams", cat: "ChatOps", status: "available", desc: "Bot notifications and adaptive cards." },
];

const KEYS = [
  { id: "AK-8291", name: "Production API", created: "2026-05-14", lastUsed: "2m ago", scopes: ["read:alerts", "write:incidents"] },
  { id: "AK-8290", name: "SIEM Sync", created: "2026-04-02", lastUsed: "1h ago", scopes: ["read:*"] },
  { id: "AK-8288", name: "Slack Bot", created: "2026-03-19", lastUsed: "12m ago", scopes: ["write:notifications"] },
];

const HOOKS = [
  { url: "https://hooks.firstbank.ng/blvck/alerts", events: ["incident.created", "incident.contained"], status: "healthy", last: "40s ago" },
  { url: "https://mtn-ghana.com/soc/webhook", events: ["threat.detected"], status: "healthy", last: "3m ago" },
  { url: "https://internal.sabs.co.za/alerts", events: ["incident.*"], status: "failing", last: "12h ago (401)" },
];

function StatusPill({ s }: { s: Status }) {
  const map = { connected: ["text-success", CheckCircle2, "Connected"], available: ["text-muted-foreground", Circle, "Available"], error: ["text-critical", XCircle, "Error"] } as const;
  const [color, Icon, label] = map[s];
  return <span className={`inline-flex items-center gap-1 text-[10px] font-mono uppercase tracking-widest ${color}`}><Icon className="h-3 w-3" />{label}</span>;
}

export default function IntegrationsPage()  {
  const [tab, setTab] = useState<"catalog" | "keys" | "webhooks" | "docs">("catalog");
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<Cat | "All">("All");
  const cats: (Cat | "All")[] = ["All", "Cloud", "Identity", "Endpoint", "SIEM", "ITSM", "ChatOps"];
  const filtered = useMemo(() => INTEGRATIONS.filter((i) => (cat === "All" || i.cat === cat) && i.name.toLowerCase().includes(q.toLowerCase())), [q, cat]);

  return (
    <>
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="text-xs font-mono uppercase tracking-widest text-cyber">INTEGRATIONS.MARKETPLACE</div>
          <h1 className="text-3xl font-display font-bold mt-1">API & Integration Marketplace</h1>
          <p className="text-sm text-muted-foreground mt-1">Wire BLVCK CYBER into your stack in minutes — 19 native integrations and open API.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Connected" value={INTEGRATIONS.filter((i) => i.status === "connected").length} tone="success" icon={Plug} />
        <StatCard label="Available" value={INTEGRATIONS.filter((i) => i.status === "available").length} tone="cyber" icon={Circle} />
        <StatCard label="Failing" value={INTEGRATIONS.filter((i) => i.status === "error").length} tone="critical" icon={XCircle} />
        <StatCard label="API Calls (24h)" value="1.28M" tone="cyber" icon={KeyRound} change="+12% WoW" trend="up" detail="API requests processed in the last 24 hours"/>
      </div>

      <div className="flex gap-1 flex-wrap border-b border-white/10">
        {[
          { k: "catalog", label: "Catalog", icon: Plug },
          { k: "keys", label: "API Keys", icon: KeyRound },
          { k: "webhooks", label: "Webhooks", icon: Webhook },
          { k: "docs", label: "API Docs", icon: BookOpen },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button key={t.k} onClick={() => setTab(t.k as typeof tab)}
              className={`px-4 py-2.5 text-xs font-mono uppercase tracking-widest inline-flex items-center gap-2 border-b-2 -mb-px
                ${tab === t.k ? "border-cyber text-cyber" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
              <Icon className="h-3.5 w-3.5" />{t.label}
            </button>
          );
        })}
      </div>

      {tab === "catalog" && (
        <>
          <div className="flex items-center gap-3 flex-wrap">
            <div className="relative flex-1 min-w-[240px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search integrations…"
                className="w-full bg-black/40 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm" />
            </div>
            <div className="flex gap-1 flex-wrap">
              {cats.map((c) => (
                <button key={c} onClick={() => setCat(c)}
                  className={`text-[10px] font-mono uppercase tracking-widest px-3 py-1.5 rounded border ${cat === c ? "bg-cyber text-black border-cyber" : "border-white/10 text-muted-foreground hover:text-foreground"}`}>{c}</button>
              ))}
            </div>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((i) => (
              <div key={i.name} className="glass p-5 flex flex-col gap-3 hover:border-cyber/40 transition">
                <div className="flex items-start justify-between">
                  <div className="h-10 w-10 rounded-lg bg-cyber/10 text-cyber grid place-items-center font-mono font-bold">{i.name.split(" ").map((w) => w[0]).slice(0, 2).join("")}</div>
                  <StatusPill s={i.status} />
                </div>
                <div>
                  <div className="font-display font-bold">{i.name}</div>
                  <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mt-0.5">{i.cat}</div>
                </div>
                <p className="text-xs text-muted-foreground flex-1">{i.desc}</p>
                <button className={`w-full rounded-lg py-2 text-xs font-mono font-semibold ${i.status === "connected" ? "border border-white/10 hover:bg-white/5" : i.status === "error" ? "bg-critical/20 text-critical border border-critical/40" : "bg-cyber text-black"}`}>
                  {i.status === "connected" ? "Configure" : i.status === "error" ? "Reconnect" : "Connect"}
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {tab === "keys" && (
        <div className="glass p-5">
          <div className="flex justify-between items-center mb-4"><div className="text-xs font-mono uppercase text-muted-foreground">API keys</div><button className="bg-cyber text-black px-3 py-1.5 rounded text-xs font-mono font-semibold">Generate new key</button></div>
          <table className="w-full text-sm">
            <thead className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              <tr className="border-b border-white/5"><th className="text-left py-2">ID</th><th className="text-left py-2">Name</th><th className="text-left py-2">Scopes</th><th className="text-left py-2">Created</th><th className="text-left py-2">Last used</th><th></th></tr>
            </thead>
            <tbody>
              {KEYS.map((k) => (
                <tr key={k.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-3 font-mono text-xs text-cyber">{k.id}</td>
                  <td className="py-3">{k.name}</td>
                  <td className="py-3"><div className="flex gap-1 flex-wrap">{k.scopes.map((s) => <span key={s} className="text-[10px] font-mono bg-white/5 px-1.5 py-0.5 rounded">{s}</span>)}</div></td>
                  <td className="py-3 text-xs text-muted-foreground">{k.created}</td>
                  <td className="py-3 text-xs">{k.lastUsed}</td>
                  <td className="py-3 text-right"><button onClick={() => { navigator.clipboard.writeText(`sk_live_${k.id}_${Math.random().toString(36).slice(2)}`); toast.success("Key copied"); }} className="text-xs font-mono text-cyber inline-flex items-center gap-1"><Copy className="h-3 w-3" />Copy</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "webhooks" && (
        <div className="space-y-3">
          <div className="flex justify-end"><button className="bg-cyber text-black px-3 py-1.5 rounded text-xs font-mono font-semibold">Add webhook</button></div>
          {HOOKS.map((h, i) => (
            <div key={i} className="glass p-4 flex items-center justify-between flex-wrap gap-3">
              <div>
                <div className="text-xs font-mono text-cyber">{h.url}</div>
                <div className="mt-1 flex gap-1 flex-wrap">{h.events.map((e) => <span key={e} className="text-[10px] font-mono bg-white/5 px-1.5 py-0.5 rounded">{e}</span>)}</div>
              </div>
              <div className="text-right">
                <div className={`text-[10px] font-mono uppercase tracking-widest ${h.status === "healthy" ? "text-success" : "text-critical"}`}>{h.status}</div>
                <div className="text-xs text-muted-foreground mt-0.5">Last: {h.last}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "docs" && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="glass p-5 space-y-2">
            <div className="text-xs font-mono uppercase text-muted-foreground">Endpoints</div>
            {["GET /v1/alerts", "POST /v1/incidents", "GET /v1/assets", "POST /v1/hunts", "GET /v1/threats/feed", "POST /v1/webhooks"].map((e) => (
              <div key={e} className="p-2 rounded bg-black/40 border border-white/5 text-xs font-mono text-cyber">{e}</div>
            ))}
          </div>
          <div className="glass p-5 lg:col-span-2">
            <div className="text-xs font-mono uppercase text-muted-foreground mb-2">Request example — POST /v1/incidents</div>
            <pre className="bg-black/60 border border-white/10 rounded p-4 text-[11px] font-mono text-success overflow-x-auto">{`curl https://api.blvck.cyber/v1/incidents \\
  -H "Authorization: Bearer sk_live_…" \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Suspicious LSASS access on DC01",
    "severity": "critical",
    "assets": ["DC01.corp.local"],
    "playbook": "credential_dump_response"
  }'
`}</pre>
            <div className="text-xs font-mono uppercase text-muted-foreground mt-4 mb-2">Response</div>
            <pre className="bg-black/60 border border-white/10 rounded p-4 text-[11px] font-mono text-cyber overflow-x-auto">{`{
  "id": "INC-2026-4421",
  "status": "triaging",
  "assignee": "auto",
  "created_at": "2026-07-22T09:14:04Z"
}`}</pre>
          </div>
        </div>
      )}
    </>
  );
}
