'use client'

import {
  BrainCircuit,
  Settings,
  SlidersHorizontal,
  Database,
  ShieldCheck,
  Workflow,
  Cpu,
  Save,
} from 'lucide-react'
import { useState } from 'react'

const aiModels = [
  {
    name: 'BLVCK Security AI Core',
    provider: 'Internal AI Engine',
    status: 'Active',
    version: 'v2.4.1',
  },
  {
    name: 'Threat Intelligence Model',
    provider: 'External Intelligence Feed',
    status: 'Active',
    version: 'v1.8.0',
  },
]

const dataSources = [
  'Security Logs',
  'Firewall Events',
  'Endpoint Telemetry',
  'Threat Intelligence Feeds',
  'Vulnerability Scanner',
]

const automationRules = [
  {
    name: 'Critical Threat Detection',
    description:
      'Automatically analyze and prioritize critical security alerts.',
    enabled: true,
  },
  {
    name: 'Incident Summarization',
    description: 'Generate AI summaries for security incidents.',
    enabled: true,
  },
  {
    name: 'Threat Hunting Suggestions',
    description: 'Recommend investigation paths to analysts.',
    enabled: false,
  },
]

export function AIConfigModule() {
  const [confidence, setConfidence] = useState(85)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div
          className="
          rounded-lg
          bg-primary/10
          p-3
        "
        >
          <Settings className="h-6 w-6 text-primary" />
        </div>

        <div>
          <h1 className="text-xl font-semibold">AI Configuration</h1>

          <p
            className="
            text-sm
            text-muted-foreground
          "
          >
            Configure artificial intelligence security operations
          </p>
        </div>
      </div>

      {/* AI Engine */}
      <div
        className="
        rounded-xl
        border
        bg-card
        p-5
      "
      >
        <div
          className="
          mb-4
          flex
          items-center
          gap-3
        "
        >
          <BrainCircuit className="h-5 w-5 text-primary" />

          <h2 className="font-semibold">AI Engine Configuration</h2>
        </div>

        <div
          className="
          grid
          gap-4
          md:grid-cols-2
        "
        >
          {aiModels.map((model) => (
            <div
              key={model.name}
              className="
                rounded-lg
                border
                p-4
              "
            >
              <div
                className="
                flex
                items-center
                justify-between
              "
              >
                <h3 className="font-medium">{model.name}</h3>

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
                  {model.status}
                </span>
              </div>

              <p
                className="
                mt-2
                text-sm
                text-muted-foreground
              "
              >
                {model.provider}
              </p>

              <p
                className="
                text-xs
                text-muted-foreground
              "
              >
                Version {model.version}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Confidence Threshold */}
      <div
        className="
        rounded-xl
        border
        bg-card
        p-5
      "
      >
        <div
          className="
          flex
          items-center
          gap-3
          mb-4
        "
        >
          <SlidersHorizontal className="h-5 w-5 text-primary" />

          <h2 className="font-semibold">AI Decision Threshold</h2>
        </div>

        <p
          className="
          text-sm
          text-muted-foreground
        "
        >
          Minimum confidence level before AI recommendations are triggered.
        </p>

        <div className="mt-5">
          <input
            type="range"
            min="0"
            max="100"
            value={confidence}
            onChange={(e) => setConfidence(Number(e.target.value))}
            className="w-full"
          />

          <div
            className="
            mt-2
            flex
            justify-between
            text-sm
          "
          >
            <span>Confidence</span>

            <span className="font-semibold">{confidence}%</span>
          </div>
        </div>
      </div>

      {/* Data Sources */}
      <div
        className="
        rounded-xl
        border
        bg-card
        p-5
      "
      >
        <div
          className="
          mb-4
          flex
          items-center
          gap-3
        "
        >
          <Database className="h-5 w-5 text-primary" />

          <h2 className="font-semibold">AI Data Sources</h2>
        </div>

        <div
          className="
          grid
          gap-3
          md:grid-cols-2
        "
        >
          {dataSources.map((source) => (
            <div
              key={source}
              className="
                flex
                items-center
                gap-3
                rounded-lg
                border
                p-3
              "
            >
              <ShieldCheck className="h-4 w-4 text-primary" />

              <span className="text-sm">{source}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Automation */}
      <div
        className="
        rounded-xl
        border
        bg-card
        p-5
      "
      >
        <div
          className="
          mb-4
          flex
          items-center
          gap-3
        "
        >
          <Workflow className="h-5 w-5 text-primary" />

          <h2 className="font-semibold">Automation Rules</h2>
        </div>

        <div className="space-y-3">
          {automationRules.map((rule) => (
            <div
              key={rule.name}
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
                <h3 className="text-sm font-medium">{rule.name}</h3>

                <p
                  className="
                  text-xs
                  text-muted-foreground
                "
                >
                  {rule.description}
                </p>
              </div>

              <span
                className={
                  rule.enabled
                    ? `
                      rounded-full
                      bg-primary/10
                      px-3
                      py-1
                      text-xs
                      text-primary
                    `
                    : `
                      rounded-full
                      bg-muted
                      px-3
                      py-1
                      text-xs
                      text-muted-foreground
                    `
                }
              >
                {rule.enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Save */}
      <button
        className="
          inline-flex
          items-center
          gap-2
          rounded-lg
          bg-primary
          px-4
          py-2
          text-sm
          font-medium
          text-primary-foreground
          hover:opacity-90
        "
      >
        <Save className="h-4 w-4" />
        Save AI Configuration
      </button>
    </div>
  )
}
