'use client'

import {
  Bot,
  BrainCircuit,
  MessageSquare,
  ShieldCheck,
  Sparkles,
  Activity,
  AlertTriangle,
  Search,
} from 'lucide-react'

const aiCapabilities = [
  {
    title: 'Threat Analysis',
    description:
      'AI analyzes security events and identifies potential threats across your environment.',
    icon: ShieldCheck,
    status: 'Active',
  },
  {
    title: 'Security Recommendations',
    description:
      'Provides automated recommendations based on vulnerabilities, alerts, and incidents.',
    icon: Sparkles,
    status: 'Active',
  },
  {
    title: 'Threat Hunting Assistant',
    description:
      'Helps analysts investigate suspicious activity using natural language queries.',
    icon: Search,
    status: 'Beta',
  },
  {
    title: 'Incident Investigation',
    description: 'Summarizes incidents and assists with response workflows.',
    icon: AlertTriangle,
    status: 'Active',
  },
]

const mockQueries = [
  {
    question: 'Show me critical threats from the last 24 hours',
    answer:
      'Detected 3 critical events involving suspicious login activity and malware indicators.',
  },
  {
    question: 'Which assets require attention?',
    answer: '5 assets have high-risk vulnerabilities requiring remediation.',
  },
]

export function AIAssistantModule() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-primary/10 p-3">
          <Bot className="h-6 w-6 text-primary" />
        </div>

        <div>
          <h1 className="text-xl font-semibold">AI Security Assistant</h1>

          <p className="text-sm text-muted-foreground">
            AI-powered cybersecurity analysis and assistance
          </p>
        </div>
      </div>

      {/* AI Status */}
      <div
        className="
        grid
        gap-4
        md:grid-cols-3
      "
      >
        <div className="rounded-xl border bg-card p-5">
          <div className="flex items-center gap-3">
            <BrainCircuit className="h-5 w-5 text-primary" />

            <span className="text-sm font-medium">AI Engine</span>
          </div>

          <p className="mt-3 text-2xl font-bold">Online</p>

          <p className="text-xs text-muted-foreground">
            Model monitoring active
          </p>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <div className="flex items-center gap-3">
            <Activity className="h-5 w-5 text-primary" />

            <span className="text-sm font-medium">Analysis Events</span>
          </div>

          <p className="mt-3 text-2xl font-bold">12,482</p>

          <p className="text-xs text-muted-foreground">
            Events processed today
          </p>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <div className="flex items-center gap-3">
            <MessageSquare className="h-5 w-5 text-primary" />

            <span className="text-sm font-medium">Assistant Queries</span>
          </div>

          <p className="mt-3 text-2xl font-bold">248</p>

          <p className="text-xs text-muted-foreground">Analyst interactions</p>
        </div>
      </div>

      {/* Capabilities */}
      <div className="rounded-xl border bg-card">
        <div className="border-b p-5">
          <h2 className="font-semibold">AI Capabilities</h2>
        </div>

        <div
          className="
          grid
          gap-4
          p-5
          md:grid-cols-2
        "
        >
          {aiCapabilities.map((item) => {
            const Icon = item.icon

            return (
              <div
                key={item.title}
                className="
                  rounded-lg
                  border
                  p-4
                  transition
                  hover:bg-muted/40
                "
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon className="h-5 w-5 text-primary" />

                    <h3 className="font-medium">{item.title}</h3>
                  </div>

                  <span
                    className="
                    rounded-full
                    bg-primary/10
                    px-2
                    py-1
                    text-xs
                    text-primary
                  "
                  >
                    {item.status}
                  </span>
                </div>

                <p
                  className="
                  mt-3
                  text-sm
                  text-muted-foreground
                "
                >
                  {item.description}
                </p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Mock AI Chat */}
      <div className="rounded-xl border bg-card">
        <div className="border-b p-5">
          <h2 className="font-semibold">Recent AI Conversations</h2>
        </div>

        <div className="space-y-4 p-5">
          {mockQueries.map((item, index) => (
            <div
              key={index}
              className="
                rounded-lg
                border
                p-4
              "
            >
              <p className="text-sm font-medium">Q: {item.question}</p>

              <p
                className="
                mt-2
                text-sm
                text-muted-foreground
              "
              >
                AI: {item.answer}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
