"use client";

import { useState } from "react";
import {
  Bell,
  Shield,
  Smartphone,
  MessageSquareText,
  CheckCircle2,
  XCircle,
  Download,
  Activity,
} from "lucide-react";

import { StatCard } from "@/components/shell/stat-card";
import { toast } from "sonner";

export default function MobilePage() {
  const [push, setPush] = useState({
    critical: true,
    high: true,
    medium: false,
    low: false,
    digest: true,
  });

  const [chat, setChat] = useState<
    { role: "u" | "a"; text: string }[]
  >([
    {
      role: "a",
      text: "Hi Kofi — I'm your BLVCK AI analyst. What can I check for you?",
    },
  ]);

  const [msg, setMsg] = useState("");

  const install = () =>
    toast.success(
      "Install prompt available in production build. Add to Home Screen from your browser share menu."
    );

  const send = () => {
    if (!msg.trim()) return;

    setChat((c) => [
      ...c,
      { role: "u", text: msg },
      {
        role: "a",
        text: `Checked: no matching indicators in the last 24h for "${msg.slice(
          0,
          42
        )}". Want me to open a hunt?`,
      },
    ]);

    setMsg("");
  };

  return (
    <>
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="text-xs font-mono uppercase tracking-widest text-cyber">
            MOBILE.PWA
          </div>

          <h1 className="text-3xl font-display font-bold mt-1">
            Mobile & Progressive Web App
          </h1>

          <p className="text-sm text-muted-foreground mt-1">
            Installable on iOS and Android — same auth, same session, offline
            shell.
          </p>
        </div>

        <button
          onClick={install}
          className="bg-cyber text-black rounded-lg px-4 py-2 text-xs font-mono font-semibold inline-flex items-center gap-2"
        >
          <Download className="h-3.5 w-3.5" />
          Install on device
        </button>
      </div>


      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

        <StatCard
          label="Active devices"
          value="412"
          tone="cyber"
          icon={Smartphone}
          change="+38 this month"
          trend="up"
          detail="Registered mobile endpoints"
        />

        <StatCard
          label="Pushes sent (24h)"
          value="2,184"
          tone="success"
          icon={Bell}
          change="Live notifications"
          trend="up"
          detail="Security notifications delivered"
        />

        <StatCard
          label="Mobile approvals"
          value="64"
          tone="warning"
          icon={CheckCircle2}
          change="18 pending"
          trend="up"
          detail="Incident approvals awaiting action"
        />

        <StatCard
          label="Session security"
          value="A+"
          tone="success"
          icon={Shield}
          change="Protected"
          trend="up"
          detail="Mobile authentication posture"
        />

      </div>


      <div className="grid lg:grid-cols-[380px_1fr] gap-6">

        <div className="mx-auto lg:mx-0">

          <div className="w-[340px] h-[680px] rounded-[42px] border-[10px] border-white/10 bg-black shadow-[0_40px_100px_-20px_rgba(0,212,255,0.35)] p-3 relative overflow-hidden">

            <div className="absolute top-2 left-1/2 -translate-x-1/2 h-5 w-28 bg-black rounded-full z-10"/>

            <div className="h-full w-full rounded-[30px] overflow-hidden bg-gradient-to-b from-[#05080d] to-black flex flex-col">

              <div className="p-4 pt-8 text-[10px] font-mono flex justify-between text-muted-foreground">
                <span>9:41</span>
                <span>●●●● 5G</span>
              </div>


              <div className="px-4">

                <div className="text-[10px] font-mono text-cyber uppercase tracking-widest">
                  Security Posture
                </div>

                <div className="mt-1 flex items-end gap-2">
                  <div className="text-5xl font-display font-bold text-cyber">
                    87
                  </div>
                  <div className="text-xs text-muted-foreground mb-2">
                    /100
                  </div>
                </div>

                <div className="text-[10px] text-success mt-1">
                  ▲ +4 this week
                </div>

              </div>


              <div className="mt-3 mx-4 rounded-xl border border-cyber/30 bg-cyber/5 p-3">

                <div className="text-[10px] font-mono uppercase text-cyber">
                  Awaiting approval
                </div>

                <div className="text-xs mt-1">
                  Isolate DC01 following credential dump alert
                </div>

                <div className="mt-2 flex gap-2">

                  <button className="flex-1 bg-cyber text-black rounded py-1.5 text-[10px] font-semibold">
                    Approve
                  </button>

                  <button className="flex-1 border border-white/10 rounded py-1.5 text-[10px]">
                    Deny
                  </button>

                </div>

              </div>


              <div className="mt-3 mx-4 text-[10px] font-mono uppercase text-muted-foreground">
                Live alerts
              </div>


              <div className="mt-1 mx-4 space-y-1.5 flex-1 overflow-hidden">

                {[
                  {
                    t:"Critical",
                    c:"text-critical",
                    d:"Ransomware beacon — First Bank NG"
                  },
                  {
                    t:"High",
                    c:"text-warning",
                    d:"Impossible travel — CFO@mtn.gh"
                  },
                  {
                    t:"Medium",
                    c:"text-cyber",
                    d:"New service on 3 endpoints"
                  },
                  {
                    t:"Low",
                    c:"text-success",
                    d:"Patch applied to 214 hosts"
                  }
                ].map((a,i)=>(
                  <div
                    key={i}
                    className="p-2 rounded bg-black/50 border border-white/5"
                  >
                    <div className={`text-[9px] font-mono uppercase ${a.c}`}>
                      {a.t}
                    </div>
                    <div className="text-[11px]">
                      {a.d}
                    </div>
                  </div>
                ))}

              </div>


              <div className="mx-4 mb-4 mt-2 h-11 rounded-full bg-cyber/10 border border-cyber/30 grid grid-cols-4 text-cyber">

                {[Activity,Bell,MessageSquareText,Shield].map(
                  (I,i)=>(
                    <div key={i} className="grid place-items-center">
                      <I className="h-4 w-4"/>
                    </div>
                  )
                )}

              </div>


            </div>
          </div>

        </div>


        <div className="space-y-6">

          <div className="glass p-5">

            <div className="text-xs font-mono uppercase text-muted-foreground">
              Push notification settings
            </div>


            <div className="mt-3 divide-y divide-white/5">

              {(Object.keys(push) as (keyof typeof push)[]).map((k)=>(

                <label
                  key={k}
                  className="flex items-center justify-between py-3 cursor-pointer"
                >

                  <div>

                    <div className="text-sm capitalize">
                      {k==="digest"
                        ?"Daily digest"
                        :`${k} severity alerts`}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      {k==="digest"
                        ?"Morning summary at 07:00 local"
                        :`Push instantly when a ${k} alert fires`}
                    </div>

                  </div>


                  <button
                    onClick={() =>
                      setPush((p)=>({
                        ...p,
                        [k]:!p[k]
                      }))
                    }
                    className={`relative h-6 w-11 rounded-full ${
                      push[k]
                        ?"bg-cyber"
                        :"bg-white/10"
                    }`}
                  >

                    <span
                      className={`absolute top-0.5 h-5 w-5 rounded-full bg-black ${
                        push[k]
                          ?"left-5"
                          :"left-0.5"
                      }`}
                    />

                  </button>


                </label>

              ))}

            </div>

          </div>


          <div className="glass p-5 flex flex-col h-[420px]">

            <div className="text-xs font-mono uppercase text-muted-foreground flex items-center gap-2">
              <MessageSquareText className="h-3.5 w-3.5"/>
              AI Analyst — mobile chat preview
            </div>


            <div className="mt-3 flex-1 overflow-y-auto space-y-2">

              {chat.map((m,i)=>(
                <div
                  key={i}
                  className={`max-w-[80%] p-2.5 rounded-lg text-sm ${
                    m.role==="a"
                    ?"bg-cyber/10 border border-cyber/20"
                    :"bg-white/5 ml-auto"
                  }`}
                >
                  {m.text}
                </div>
              ))}

            </div>


            <div className="mt-3 flex gap-2">

              <input
                value={msg}
                onChange={(e)=>setMsg(e.target.value)}
                onKeyDown={(e)=>e.key==="Enter"&&send()}
                placeholder="Ask about an incident..."
                className="flex-1 bg-black/40 border border-white/10 rounded px-3 py-2 text-sm"
              />


              <button
                onClick={send}
                className="bg-cyber text-black px-4 rounded text-xs font-mono font-semibold"
              >
                Send
              </button>

            </div>

          </div>


          <div className="glass p-5">

            <div className="text-xs font-mono uppercase text-muted-foreground">
              Device health across enrolled fleet
            </div>


            <div className="mt-3 grid grid-cols-3 gap-3 text-center">

              <div>
                <div className="text-2xl font-display font-bold text-success">
                  98%
                </div>
                <div className="text-xs text-muted-foreground">
                  Encrypted
                </div>
              </div>


              <div>
                <div className="text-2xl font-display font-bold text-cyber">
                  94%
                </div>
                <div className="text-xs text-muted-foreground">
                  MDM enrolled
                </div>
              </div>


              <div>
                <div className="text-2xl font-display font-bold text-warning">
                  6%
                </div>
                <div className="text-xs text-muted-foreground">
                  OS outdated
                </div>
              </div>

            </div>


            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">

              <XCircle className="h-4 w-4 text-critical"/>

              3 devices flagged as jailbroken — auto-quarantined

            </div>

          </div>

        </div>

      </div>
    </>
  );
}