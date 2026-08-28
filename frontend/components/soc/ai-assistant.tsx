"use client"

import { useEffect, useRef, useState } from "react"
import { Bot, Send, User } from "lucide-react"
import { Panel } from "./panel"
import { cn } from "@/lib/utils"

interface Msg {
  role: "ai" | "user"
  text: string
}

const suggestions = [
  "Summarize the current active incidents and suggest next steps",
  "Which MITRE techniques have the weakest detection coverage right now?",
  "Explain the top priority alert and its affected asset",
]

const responses: Record<string, string> = {
  "Explain the top critical threat":
    "Your most urgent issue is a suspected ransomware attempt on core-banking-db-01. My behavioral engine spotted rapid file-encryption activity and automatically isolated the host before spread. In plain terms: an attacker tried to lock your banking data for ransom — I blocked it, but you should confirm backups are intact and rotate exposed credentials.",
  "What should I fix first?":
    "Priority order: (1) Patch CVE-2024-3094 on the VPN concentrator — it's a critical backdoor with a public exploit. (2) Encrypt the 3 unencrypted data volumes flagged in Health Monitoring. (3) Remediate the MOVEit SQL injection on your banking database. Doing (1) and (2) alone should raise your security score by about 9 points.",
  "Summarize today's security posture":
    "Overall score is 78/100 (Moderate). We blocked 8,300+ attacks in the last 24h with 99.3% auto-mitigated. There are 14 active threats (4 critical) and 27 open vulnerabilities. Network stability on edge-3 is degraded and data protection needs attention. No confirmed breach — the environment is contained but has fixable gaps.",
  "Is my banking database safe?":
    "core-banking-db-01 is currently protected but under pressure. I blocked a ransomware attempt and an SQL-injection probe against it today. It still has one high-severity MOVEit vulnerability (CVE-2023-34362) that is being remediated. I recommend prioritizing that patch and enabling query-level anomaly alerts, which I can automate for you.",
}

const defaultReply =
  "I've analyzed your environment. I can explain any threat in plain language, recommend remediation steps, run scans, or draft an incident report. Try one of the suggested questions to see how I reason about your security posture."

export function AIAssistant() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "ai",
      text: "Hi Amara — I'm your AI Security Analyst. I'm monitoring Zenith Bank Group in real time. Ask me anything about your threats, vulnerabilities, or posture.",
    },
  ])
  const [input, setInput] = useState("")
  const [typing, setTyping] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, typing])

  const send = (text: string) => {
    const q = text.trim()
    if (!q || typing) return
    setMessages((m) => [...m, { role: "user", text: q }])
    setInput("")
    setTyping(true)
    setTimeout(() => {
      setMessages((m) => [...m, { role: "ai", text: responses[q] ?? defaultReply }])
      setTyping(false)
    }, 900)
  }

  return (
    <Panel
      title="AI Security Analyst"
      icon={<Bot className="h-4 w-4" />}
      bodyClassName="flex flex-col p-0"
      className="h-full"
      action={
        <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-success">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-success" /> Online
        </span>
      }
    >
      <div className="flex max-h-[360px] min-h-[240px] flex-1 flex-col gap-3 overflow-y-auto p-4">
        {messages.map((m, i) => (
          <div key={i} className={cn("flex gap-2.5", m.role === "user" && "flex-row-reverse")}>
            <div
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-md",
                m.role === "ai" ? "bg-primary/15 text-primary" : "bg-secondary text-foreground",
              )}
            >
              {m.role === "ai" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
            </div>
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-3 py-2 text-xs leading-relaxed",
                m.role === "ai"
                  ? "bg-secondary/60 text-foreground"
                  : "bg-primary/15 text-foreground",
              )}
            >
              {m.text}
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/15 text-primary">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-1 rounded-lg bg-secondary/60 px-3 py-3">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t border-border p-3">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              disabled={typing}
              className="rounded-full border border-border px-2.5 py-1 font-mono text-[10px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.nativeEvent.isComposing && e.keyCode !== 229) send(input)
            }}
            placeholder="Ask your AI analyst…"
            className="flex-1 rounded-md border border-border bg-background/60 px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none"
          />
          <button
            onClick={() => send(input)}
            disabled={typing || !input.trim()}
            className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-40"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </Panel>
  )
}
