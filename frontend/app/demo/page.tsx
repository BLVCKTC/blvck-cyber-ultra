"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { toast } from "sonner";
import { ArrowLeft, CheckCircle2, ShieldCheck } from "lucide-react";
import { AFRICAN_COUNTRIES, INDUSTRIES } from "@/lib/mock-data";
import { ParticleField } from "@/components/particle-field";

const CHALLENGES = [
  "Ransomware",
  "Phishing",
  "Insider Threat",
  "Cloud Security",
  "Compliance (POPIA/NDPA/PCI)",
  "DDoS",
  "APT / Nation-state",
  "IoT / OT Security",
];

const schema = z.object({
  company: z.string().min(2, "Company required"),
  contact: z.string().min(2, "Contact name required"),
  email: z.string().email("Valid business email required"),
  phone: z.string().min(6, "Phone required"),
  industry: z.string().min(1, "Industry required"),
  size: z.string().min(1, "Size required"),
  country: z.string().min(1, "Country required"),
  challenges: z.array(z.string()).min(1, "Select at least one"),
  demoDate: z.string().min(1, "Preferred date required"),
  contactMethod: z.string(),
  hp: z.string().max(0, "Bot detected"),
});

export default function DemoPage() {
  const router = useRouter();
  const [state, setState] = useState({
    company: "",
    contact: "",
    email: "",
    phone: "",
    industry: "",
    size: "",
    country: "",
    challenges: [] as string[],
    demoDate: "",
    contactMethod: "Email",
    hp: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [done, setDone] = useState(false);
  const [lastSubmit, setLastSubmit] = useState(0);

  const set = <K extends keyof typeof state>(k: K, v: (typeof state)[K]) =>
    setState((s) => ({ ...s, [k]: v }));

  const toggleChallenge = (c: string) => {
    setState((s) => ({
      ...s,
      challenges: s.challenges.includes(c)
        ? s.challenges.filter((x) => x !== c)
        : [...s.challenges, c],
    }));
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (Date.now() - lastSubmit < 5000) {
      toast.error("Please slow down.");
      return;
    }
    const parsed = schema.safeParse(state);
    if (!parsed.success) {
      const errs: Record<string, string> = {};
      parsed.error.issues.forEach((i) => {
        errs[i.path[0] as string] = i.message;
      });
      setErrors(errs);
      toast.error("Please fix the highlighted fields.");
      return;
    }
    setLastSubmit(Date.now());
    setErrors({});
    setDone(true);
    toast.success("Demo request received — we'll reach out within 4 hours.");
  };

  if (done) {
    return (
      <div className="min-h-screen grid place-items-center px-4 relative overflow-hidden">
        <div className="absolute inset-0">
          <ParticleField density={40} />
        </div>
        <div className="relative glass-strong p-10 max-w-lg text-center">
          <CheckCircle2 className="h-16 w-16 text-success mx-auto" />
          <h1 className="mt-6 text-3xl font-display font-bold">Request received</h1>
          <div className="mt-2 font-mono text-xs text-cyber tracking-widest">
            REF: DR-{Date.now().toString().slice(-8)}
          </div>
          <p className="mt-4 text-muted-foreground text-sm">
            A BLVCK CYBER solutions architect will contact{" "}
            <span className="text-cyber">{state.email}</span> within 4 business
            hours to confirm your demo for{" "}
            <span className="text-cyber">{state.demoDate}</span>.
          </p>
          <div className="mt-8 flex gap-2 justify-center">
            <Link
              href="/"
              className="border border-cyber/40 text-cyber px-4 py-2 rounded-lg text-sm"
            >
              Home
            </Link>
            <button
              onClick={() => router.push("/app/soc-demo")}
              className="bg-cyber text-black font-semibold px-4 py-2 rounded-lg text-sm"
            >
              Try AI-SOC Simulator
            </button>
          </div>
        </div>
      </div>
    );
  }

  const err = (k: string) =>
    errors[k] && (
      <div className="text-xs text-critical mt-1 font-mono">{errors[k]}</div>
    );

  const input =
    "w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2.5 text-sm focus:border-cyber focus:outline-none focus:ring-1 focus:ring-cyber";

  return (
    <div className="min-h-screen relative">
      <div className="absolute inset-0 hud-grid opacity-30" />
      <div className="relative max-w-4xl mx-auto p-6 lg:p-10">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-cyber mb-6"
        >
          <ArrowLeft className="h-4 w-4" /> Back to home
        </Link>
        <div className="glass-strong p-8 lg:p-12">
          <div className="flex items-center gap-2 font-mono text-xs text-cyber tracking-widest">
            <ShieldCheck className="h-4 w-4" /> SECURE DEMO REQUEST // TLS
            ENCRYPTED
          </div>
          <h1 className="mt-3 text-4xl font-display font-bold">
            See BLVCK CYBER in your environment.
          </h1>
          <p className="mt-2 text-muted-foreground">
            30-minute live walkthrough with a solutions architect. Zero
            commitment.
          </p>

          <form
            onSubmit={submit}
            className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {/* Honeypot */}
            <input
              type="text"
              name="website"
              className="hidden"
              tabIndex={-1}
              autoComplete="off"
              value={state.hp}
              onChange={(e) => set("hp", e.target.value)}
            />

            <Field label="Company name" error={errors.company}>
              <input
                className={input}
                value={state.company}
                onChange={(e) => set("company", e.target.value)}
              />
            </Field>
            <Field label="Contact person" error={errors.contact}>
              <input
                className={input}
                value={state.contact}
                onChange={(e) => set("contact", e.target.value)}
              />
            </Field>
            <Field label="Business email" error={errors.email}>
              <input
                type="email"
                className={input}
                value={state.email}
                onChange={(e) => set("email", e.target.value)}
              />
            </Field>
            <Field label="Phone" error={errors.phone}>
              <input
                className={input}
                value={state.phone}
                onChange={(e) => set("phone", e.target.value)}
              />
            </Field>

            <Field label="Industry" error={errors.industry}>
              <select
                className={input}
                value={state.industry}
                onChange={(e) => set("industry", e.target.value)}
              >
                <option value="">Select…</option>
                {INDUSTRIES.map((i) => (
                  <option key={i}>{i}</option>
                ))}
              </select>
            </Field>
            <Field label="Organization size" error={errors.size}>
              <select
                className={input}
                value={state.size}
                onChange={(e) => set("size", e.target.value)}
              >
                <option value="">Select…</option>
                {["1-50", "51-250", "251-1,000", "1,001-5,000", "5,001-10,000", "10,000+"].map(
                  (s) => (
                    <option key={s}>{s}</option>
                  )
                )}
              </select>
            </Field>
            <Field label="Country" error={errors.country}>
              <select
                className={input}
                value={state.country}
                onChange={(e) => set("country", e.target.value)}
              >
                <option value="">Select…</option>
                {AFRICAN_COUNTRIES.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </Field>
            <Field label="Preferred demo date" error={errors.demoDate}>
              <input
                type="date"
                className={input}
                value={state.demoDate}
                onChange={(e) => set("demoDate", e.target.value)}
              />
            </Field>

            <div className="md:col-span-2">
              <label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                Security challenges (select all)
              </label>
              <div className="mt-2 flex flex-wrap gap-2">
                {CHALLENGES.map((c) => {
                  const active = state.challenges.includes(c);
                  return (
                    <button
                      type="button"
                      key={c}
                      onClick={() => toggleChallenge(c)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition ${
                        active
                          ? "bg-cyber text-black border-cyber"
                          : "border-white/10 text-muted-foreground hover:border-cyber/40"
                      }`}
                    >
                      {c}
                    </button>
                  );
                })}
              </div>
              {err("challenges")}
            </div>

            <Field label="Preferred contact method" error={errors.contactMethod}>
              <select
                className={input}
                value={state.contactMethod}
                onChange={(e) => set("contactMethod", e.target.value)}
              >
                <option>Email</option>
                <option>Phone call</option>
                <option>WhatsApp</option>
                <option>Video call</option>
              </select>
            </Field>

            <div className="md:col-span-2 mt-4 flex flex-col sm:flex-row justify-between items-center gap-3">
              <div className="text-xs text-muted-foreground">
                By submitting, you agree to be contacted by BLVCK CYBER. See our
                privacy notice.
              </div>
              <button
                type="submit"
                className="bg-cyber text-black font-semibold px-6 py-3 rounded-lg hover:brightness-110 w-full sm:w-auto"
              >
                Request demo
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  children,
  error,
}: {
  label: string;
  children: React.ReactNode;
  error?: string;
}) {
  return (
    <div>
      <label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
        {label}
      </label>
      <div className="mt-1.5">{children}</div>
      {error && (
        <div className="text-xs text-critical mt-1 font-mono">{error}</div>
      )}
    </div>
  );
}