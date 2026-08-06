"use client"

import { useState } from "react"
import { Mail, Phone, Building2, Users } from "lucide-react"
import { toast } from "sonner"
import { PageHeader } from "@/components/shell/page-header"
import { SEED_LEADS, type Lead } from "@/lib/mock-data"

const STAGES: Lead["stage"][] = ["new", "contacted", "demo-scheduled", "proposal", "won", "lost"]
const STAGE_LABEL: Record<Lead["stage"], string> = {
  new: "New",
  contacted: "Contacted",
  "demo-scheduled": "Demo Scheduled",
  proposal: "Proposal",
  won: "Won",
  lost: "Lost",
}

export default function LeadsPipelinePage() {
  const [leads, setLeads] = useState<Lead[]>(SEED_LEADS)
  const [selected, setSelected] = useState<Lead | null>(null)
  const [dragged, setDragged] = useState<string | null>(null)

  const move = (id: string, stage: Lead["stage"]) => {
    setLeads((ls) => ls.map((l) => (l.id === id ? { ...l, stage } : l)))
    toast.success(`Moved to ${STAGE_LABEL[stage]}`)
  }

  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Leads Pipeline"
        description="Sales pipeline — drag leads between stages, click a card for full detail and notes."
      />

      <div className="space-y-4 p-4 lg:p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="size-4" />
            {leads.length} leads · drag to move
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 overflow-x-auto md:grid-cols-3 lg:grid-cols-6">
          {STAGES.map((stage) => {
            const items = leads.filter((l) => l.stage === stage)
            const value = items.reduce((a, l) => a + l.value, 0)
            return (
              <div
                key={stage}
                className="min-h-[400px] rounded-lg border border-border/60 bg-secondary/20 p-3"
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => {
                  if (dragged) {
                    move(dragged, stage)
                    setDragged(null)
                  }
                }}
              >
                <div className="mb-3 border-b border-border/60 pb-2">
                  <div className="text-xs font-mono uppercase tracking-widest text-primary">
                    {STAGE_LABEL[stage]}
                  </div>
                  <div className="font-mono text-[10px] tabular-nums text-muted-foreground">
                    {items.length} · ${(value / 1000).toFixed(0)}k
                  </div>
                </div>
                <div className="space-y-2">
                  {items.map((l) => (
                    <div
                      key={l.id}
                      draggable
                      onDragStart={() => setDragged(l.id)}
                      onClick={() => setSelected(l)}
                      className="cursor-pointer rounded border border-border/60 bg-card/60 p-3 transition hover:border-primary/40"
                    >
                      <div className="truncate text-sm font-medium">{l.company}</div>
                      <div className="truncate text-xs text-muted-foreground">{l.contact}</div>
                      <div className="mt-2 flex items-center justify-between font-mono text-[10px]">
                        <span className="text-primary">{l.country}</span>
                        <span className="tabular-nums text-warning">${(l.value / 1000).toFixed(0)}k</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {selected && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="w-full max-w-2xl rounded-xl border border-border/60 bg-card p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="font-mono text-xs text-primary">{selected.id}</div>
                <h2 className="mt-1 flex items-center gap-2 font-display text-2xl font-bold">
                  <Building2 className="size-5" /> {selected.company}
                </h2>
                <div className="mt-1 text-sm text-muted-foreground">
                  {selected.industry} · {selected.country} · {selected.size}
                </div>
              </div>
              <button onClick={() => setSelected(null)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="font-mono text-[10px] uppercase text-muted-foreground">Contact</div>
                <div>{selected.contact}</div>
              </div>
              <div>
                <div className="font-mono text-[10px] uppercase text-muted-foreground">Value</div>
                <div className="font-mono tabular-nums">${selected.value.toLocaleString()}</div>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="size-3.5 text-primary" />
                <span className="text-xs">{selected.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="size-3.5 text-primary" />
                <span className="text-xs">{selected.phone}</span>
              </div>
            </div>

            <div className="mt-4">
              <div className="mb-2 font-mono text-[10px] uppercase text-muted-foreground">Challenges</div>
              <div className="flex flex-wrap gap-1.5">
                {selected.challenges.map((c) => (
                  <span
                    key={c}
                    className="rounded border border-primary/30 bg-primary/10 px-2 py-0.5 text-xs text-primary"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-4">
              <div className="mb-2 font-mono text-[10px] uppercase text-muted-foreground">Move to stage</div>
              <div className="flex flex-wrap gap-2">
                {STAGES.map((s) => (
                  <button
                    key={s}
                    onClick={() => {
                      move(selected.id, s)
                      setSelected({ ...selected, stage: s })
                    }}
                    className={`rounded border px-3 py-1 font-mono text-xs ${
                      selected.stage === s
                        ? "border-primary bg-primary text-black"
                        : "border-border/60 text-muted-foreground hover:border-primary/40"
                    }`}
                  >
                    {STAGE_LABEL[s]}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-4">
              <div className="mb-2 font-mono text-[10px] uppercase text-muted-foreground">
                Notes / Communication History
              </div>
              <div className="max-h-32 space-y-2 overflow-y-auto rounded bg-black/20 p-3 text-xs">
                {selected.notes.length === 0 ? (
                  <div className="italic text-muted-foreground">No notes yet</div>
                ) : (
                  selected.notes.map((n, i) => (
                    <div key={i}>
                      <span className="font-mono text-primary">
                        {n.date} · {n.author}:
                      </span>{" "}
                      {n.text}
                    </div>
                  ))
                )}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  placeholder="Add a note or follow-up reminder…"
                  className="flex-1 rounded border border-border/60 bg-black/20 px-3 py-1.5 text-xs outline-none focus:border-primary"
                />
                <button
                  onClick={() => toast.success("Note added")}
                  className="rounded bg-primary px-3 text-xs font-semibold text-black"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
