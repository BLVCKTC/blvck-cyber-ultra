"use client";

import {
  ShieldCheck,
  TrendingDown,
  FileCheck2,
  Handshake,
  Sparkles,
} from "lucide-react";

import { StatCard } from "@/components/shell/stat-card";


const PARTNERS = [
  {
    name: "Sanlam CyberShield",
    region: "Southern Africa",
    rating: "A",
    discount: "22%",
  },
  {
    name: "AXA Africa Cyber",
    region: "Francophone Africa",
    rating: "A+",
    discount: "18%",
  },
  {
    name: "Old Mutual Digital Cover",
    region: "SADC",
    rating: "A",
    discount: "20%",
  },
  {
    name: "Jubilee Cyber Guard",
    region: "East Africa",
    rating: "A-",
    discount: "15%",
  },
];


const POSTURE_FACTORS = [
  {
    factor: "Endpoint coverage",
    value: 94,
    target: "> 90%",
  },
  {
    factor: "Patch SLA adherence",
    value: 88,
    target: "> 85%",
  },
  {
    factor: "MFA on privileged accounts",
    value: 100,
    target: "100%",
  },
  {
    factor: "Backup / DR readiness",
    value: 76,
    target: "> 80%",
  },
  {
    factor: "Incident MTTR",
    value: 82,
    target: "> 75%",
  },
];


export default function InsuranceModule() {
  return (
    <>

      {/* HERO */}
      <div className="glass-strong p-8 relative overflow-hidden">

        <div className="hud-grid absolute inset-0 opacity-10" />

        <div className="relative grid md:grid-cols-[1fr_260px] gap-6 items-center">

          <div>

            <div className="text-xs font-mono uppercase tracking-widest text-cyber">
              CYBER.INSURANCE // PARTNER PREVIEW
            </div>


            <h1 className="text-3xl md:text-4xl font-display font-bold mt-2">
              Your posture score is your premium.
            </h1>


            <p className="text-sm text-muted-foreground mt-3 max-w-2xl">
              BLVCK CYBER continuously scores your security posture.
              Partner insurers price your cyber policy against that live
              score — stronger defense means a lower premium and faster
              underwriting.
            </p>


            <div className="mt-4 inline-flex items-center gap-2 rounded-lg border border-warning/30 bg-warning/10 text-warning text-[10px] font-mono uppercase tracking-widest px-3 py-1.5">

              <Sparkles className="h-3 w-3" />

              Business preview — real quotes ship Q4 2026

            </div>

          </div>



          <div className="rounded-2xl border border-cyber/30 bg-black/40 p-5 text-center">

            <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              Live posture score
            </div>


            <div className="text-6xl font-display font-bold text-cyber tabular mt-2">
              87
            </div>


            <div className="text-xs text-success mt-1">
              ▲ Qualifies for 22% premium reduction
            </div>

          </div>

        </div>

      </div>



      {/* STAT CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">


        <StatCard
          label="Estimated cover"
          value="$5M"
          tone="cyber"
          icon={ShieldCheck}
          change="1st-party + 3rd-party"
          trend="up"
          detail="Available cyber insurance coverage"
        />


        <StatCard
          label="Est. premium / yr"
          value="$28,400"
          tone="success"
          icon={TrendingDown}
          change="-22% posture credit"
          trend="down"
          detail="Reduced through security posture score"
        />


        <StatCard
          label="Underwriting time"
          value="48h"
          tone="cyber"
          icon={FileCheck2}
          change="vs 6-8 weeks industry"
          trend="down"
          detail="AI-assisted underwriting process"
        />


        <StatCard
          label="Partner insurers"
          value={String(PARTNERS.length)}
          tone="warning"
          icon={Handshake}
          change="Active partners"
          trend="up"
          detail="Regional cyber insurance providers"
        />


      </div>




      {/* CONTENT */}
      <div className="grid lg:grid-cols-3 gap-4 mt-6">


        {/* POSTURE */}
        <div className="lg:col-span-2 glass p-5 space-y-4">


          <div className="text-xs font-mono uppercase text-muted-foreground">
            Posture factors driving your quote
          </div>



          {POSTURE_FACTORS.map((item) => (

            <div key={item.factor}>

              <div className="flex justify-between text-xs mb-1">

                <span>
                  {item.factor}
                </span>


                <span className="font-mono text-cyber">

                  {item.value}%

                  <span className="text-muted-foreground">
                    {" "}/ {item.target}
                  </span>

                </span>

              </div>



              <div className="h-1.5 bg-black/60 rounded overflow-hidden">

                <div
                  className={`h-full ${
                    item.value >= 85
                      ? "bg-success"
                      : item.value >= 75
                        ? "bg-cyber"
                        : "bg-warning"
                  }`}
                  style={{
                    width: `${item.value}%`,
                  }}
                />

              </div>


            </div>

          ))}


        </div>





        {/* PARTNERS */}
        <div className="glass p-5 space-y-3">


          <div className="text-xs font-mono uppercase text-muted-foreground">
            Partner insurers
          </div>



          {PARTNERS.map((partner) => (

            <div
              key={partner.name}
              className="p-3 rounded bg-black/40 border border-white/5"
            >

              <div className="flex justify-between">

                <span className="font-semibold text-sm">
                  {partner.name}
                </span>


                <span className="text-[10px] font-mono text-cyber">
                  {partner.rating}
                </span>

              </div>


              <div className="text-[10px] text-muted-foreground mt-0.5">
                {partner.region}
              </div>


              <div className="text-[10px] font-mono text-success mt-1">

                -{partner.discount} posture credit available

              </div>


            </div>

          ))}



          <button
            className="
              w-full 
              mt-2 
              bg-cyber 
              text-black 
              rounded-lg 
              py-2 
              text-xs 
              font-mono 
              font-semibold
            "
          >
            Request partner referral
          </button>


        </div>


      </div>


    </>
  );
}