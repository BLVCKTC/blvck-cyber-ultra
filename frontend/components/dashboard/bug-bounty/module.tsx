"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Shield,
  Bug,
  CheckCircle2,
  ArrowLeft,
} from "lucide-react";
import { toast } from "sonner";
import { z } from "zod";

const submissionSchema = z.object({
  reporter: z.string().trim().min(2).max(100),
  email: z.string().trim().email().max(255),
  title: z.string().trim().min(8).max(140),
  target: z.string().trim().min(3).max(120),
  factor_target: z.enum([
    "single-tenant",
    "shared-infra",
  ]),
  factor_access_required: z.enum([
    "remote",
    "local-net",
    "authenticated",
    "physical",
  ]),
  factor_access_gained: z.enum([
    "own-data",
    "cross-tenant",
    "platform-control",
  ]),
  factor_scale: z.enum([
    "manual",
    "semi-auto",
    "mass-auto",
  ]),
  factor_persistence: z.enum([
    "session",
    "restart",
    "permanent",
  ]),
  writeup: z.string().trim().min(30).max(4000),
  hp: z.string().max(0).optional(),
});


const FACTORS = [
  {
    key: "factor_target",
    label: "Target",
    help: "Does this affect one customer's data, or shared platform infrastructure?",
    opts: [
      ["single-tenant", "Single customer / tenant"],
      ["shared-infra", "Shared platform infrastructure"],
    ],
  },
  {
    key: "factor_access_required",
    label: "Access required",
    help: "What attacker position is required?",
    opts: [
      ["remote", "Remote / internet"],
      ["local-net", "Local network"],
      ["authenticated", "Authenticated user"],
      ["physical", "Physical access"],
    ],
  },
  {
    key: "factor_access_gained",
    label: "Access gained",
    help: "What does exploitation grant?",
    opts: [
      ["own-data", "Access to own account only"],
      ["cross-tenant", "Cross-tenant data exposure"],
      ["platform-control", "Platform-wide control"],
    ],
  },
  {
    key: "factor_scale",
    label: "Scale",
    help: "How easily can this be automated?",
    opts: [
      ["manual", "One tenant at a time"],
      ["semi-auto", "Scripted per tenant"],
      ["mass-auto", "Fully automatable across all tenants"],
    ],
  },
  {
    key: "factor_persistence",
    label: "Persistence",
    help: "Does the exploit survive a session refresh or restart?",
    opts: [
      ["session", "Ends with session"],
      ["restart", "Survives session, not restart"],
      ["permanent", "Persistent / long-lived"],
    ],
  },
] as const;



export default function BugBountyModule() {

  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<Record<string,string>>({});


  const onSubmit = (
    e: React.FormEvent<HTMLFormElement>
  ) => {

    e.preventDefault();

    const fd = new FormData(e.currentTarget);

    const parsed = submissionSchema.safeParse(
      Object.fromEntries(fd)
    );


    if (!parsed.success) {

      const errs: Record<string,string> = {};

      for (const issue of parsed.error.issues) {
        errs[issue.path.join(".")] = issue.message;
      }

      setErrors(errs);

      toast.error(
        "Please review the form"
      );

      return;
    }


    if (parsed.data.hp) return;


    setErrors({});
    setSubmitted(true);


    toast.success(
      "Disclosure received — you'll hear from security@blvck.one within 48h."
    );
  };



  if (submitted) {

    return (
      <div className="min-h-screen grid place-items-center p-6">

        <div className="glass-strong p-10 max-w-md text-center">

          <CheckCircle2
            className="h-14 w-14 text-success mx-auto"
          />

          <h1 className="mt-4 text-2xl font-display font-bold">
            Report received
          </h1>


          <p className="mt-2 text-sm text-muted-foreground">
            Thank you for helping keep BLVCK CYBER — and every
            African organization we defend — safer.
            Our security team will confirm receipt within 48 hours.
          </p>


          <Link
            href="/"
            className="mt-6 inline-flex items-center gap-2 text-cyber text-sm font-mono"
          >
            <ArrowLeft className="h-4 w-4"/>
            Return home
          </Link>

        </div>

      </div>
    );
  }



  return (

    <div className="min-h-screen">


      <header className="border-b border-white/5 bg-black/60 backdrop-blur-xl sticky top-0 z-10">

        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">


          <Link
            href="/"
            className="flex items-center gap-2 text-sm font-mono text-muted-foreground hover:text-cyber"
          >
            <ArrowLeft className="h-4 w-4"/>
            BLVCK CYBER
          </Link>


          <a
            href="#submit"
            className="text-xs font-mono px-4 py-2 rounded-lg bg-cyber text-black font-semibold"
          >
            Submit a report
          </a>


        </div>

      </header>


      <section className="max-w-6xl mx-auto px-6 py-16">

        <div className="text-xs font-mono uppercase tracking-widest text-cyber">
          RESPONSIBLE DISCLOSURE // BLVCK ONE SECURITY
        </div>


        <h1 className="text-4xl md:text-5xl font-display font-bold mt-3 max-w-3xl">
          Find a vulnerability. Get paid. Help defend the continent.
        </h1>


        <p className="mt-4 text-muted-foreground max-w-2xl">
          We run coordinated disclosure with security researchers globally.
          Report a real issue in scope and we'll triage in 48h, patch fast,
          and pay bounties tied to real business risk.
        </p>

      </section>


      <section className="max-w-6xl mx-auto px-6 pb-8 grid md:grid-cols-3 gap-4">

        {[
          {
            label:"In scope",
            value:"*.blvck.cyber, *.blvck.one, mobile PWA",
            icon:Shield
          },
          {
            label:"Response SLA",
            value:"< 48 hours acknowledgement",
            icon:Bug
          },
          {
            label:"Bounty range",
            value:"$150 – $25,000 USD",
            icon:CheckCircle2
          },

        ].map((s)=>{

          const Icon=s.icon;

          return (

            <div
              key={s.label}
              className="glass p-5"
            >

              <Icon className="h-5 w-5 text-cyber"/>

              <div className="mt-3 text-[10px] uppercase tracking-widest text-muted-foreground">
                {s.label}
              </div>

              <div className="mt-1 text-sm">
                {s.value}
              </div>

            </div>

          );

        })}

      </section>


      <section className="max-w-6xl mx-auto px-6 py-10">

        <h2 className="text-2xl font-display font-bold">
          Severity Framework
        </h2>


        <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-5 gap-3">

          {FACTORS.map((f,i)=>(

            <div
              key={f.key}
              className="glass p-4"
            >

              <div className="text-[10px] text-cyber">
                FACTOR {i+1}
              </div>


              <div className="font-bold mt-1">
                {f.label}
              </div>


              <p className="text-xs text-muted-foreground mt-2">
                {f.help}
              </p>


              {f.opts.map(([v,l])=>(

                <div
                  key={v}
                  className="text-[11px] mt-2 font-mono text-muted-foreground"
                >
                  · {l}
                </div>

              ))}


            </div>

          ))}

        </div>

      </section>



      <section
        id="submit"
        className="max-w-3xl mx-auto px-6 py-16"
      >

        <h2 className="text-3xl font-display font-bold">
          Submit a vulnerability
        </h2>


        <form
          onSubmit={onSubmit}
          className="mt-6 glass-strong p-6 space-y-4"
        >

          <input
            name="hp"
            className="hidden"
            autoComplete="off"
          />


          <input
            name="reporter"
            placeholder="Your name"
            className="w-full bg-black/40 border border-white/10 rounded px-3 py-2"
          />


          <input
            name="email"
            placeholder="Email"
            className="w-full bg-black/40 border border-white/10 rounded px-3 py-2"
          />


          <input
            name="title"
            placeholder="Issue title"
            className="w-full bg-black/40 border border-white/10 rounded px-3 py-2"
          />


          <input
            name="target"
            placeholder="Affected asset / URL"
            className="w-full bg-black/40 border border-white/10 rounded px-3 py-2"
          />


          {FACTORS.map(f=>(

            <select
              key={f.key}
              name={f.key}
              defaultValue={f.opts[0][0]}
              className="w-full bg-black/40 border border-white/10 rounded px-3 py-2"
            >

              {f.opts.map(([v,l])=>(

                <option key={v} value={v}>
                  {l}
                </option>

              ))}

            </select>

          ))}



          <textarea
            name="writeup"
            rows={8}
            placeholder="Steps to reproduce, PoC, impact"
            className="w-full bg-black/40 border border-white/10 rounded p-3"
          />


          <button
            className="w-full bg-cyber text-black rounded-lg py-3 font-semibold"
          >
            Submit disclosure
          </button>


        </form>


      </section>


    </div>

  );
}