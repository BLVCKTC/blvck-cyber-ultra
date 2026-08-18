"use client";

import {
  GraduationCap,
  Award,
  PlayCircle,
  Trophy,
  Users,
  BookOpen,
} from "lucide-react";

import { StatCard } from "@/components/shell/stat-card";


const COURSES = [
  {
    title: "SOC Analyst Fundamentals",
    level: "Beginner",
    hours: 12,
    progress: 100,
    cert: "BLVCK-SOC-1",
    enrolled: 2841,
  },
  {
    title: "Incident Response for African Banks",
    level: "Intermediate",
    hours: 18,
    progress: 62,
    cert: "BLVCK-IR-B",
    enrolled: 1204,
  },
  {
    title: "Threat Hunting with MITRE ATT&CK",
    level: "Advanced",
    hours: 24,
    progress: 20,
    cert: "BLVCK-HUNT-2",
    enrolled: 812,
  },
  {
    title: "Cloud Security — AWS/Azure/GCP",
    level: "Intermediate",
    hours: 16,
    progress: 0,
    cert: "BLVCK-CLD-1",
    enrolled: 1522,
  },
  {
    title: "Mobile Money Fraud Investigation",
    level: "Advanced",
    hours: 14,
    progress: 0,
    cert: "BLVCK-MM-1",
    enrolled: 442,
  },
  {
    title: "POPIA & NDPA Compliance Deep Dive",
    level: "Beginner",
    hours: 8,
    progress: 45,
    cert: "BLVCK-REG-A",
    enrolled: 3122,
  },
];


const BADGES = [
  { name: "SOC Analyst I", earned: true },
  { name: "Incident Handler", earned: true },
  { name: "Threat Hunter", earned: false },
  { name: "Cloud Defender", earned: false },
  { name: "Forensics Practitioner", earned: false },
  { name: "Compliance Champion", earned: true },
];


export function AcademyModule() {

  return (
    <div className="space-y-6">

      <div className="glass-strong p-8 relative overflow-hidden">

        <div className="hud-grid absolute inset-0 opacity-10" />

        <div className="relative flex items-start justify-between flex-wrap gap-4">

          <div className="max-w-2xl">

            <div className="text-xs font-mono uppercase tracking-widest text-cyber">
              BLVCK ACADEMY // AFRICA-FIRST CYBER SKILLS
            </div>


            <h1 className="text-3xl md:text-4xl font-display font-bold mt-2">
              Train the defenders Africa needs.
            </h1>


            <p className="text-sm text-muted-foreground mt-3">
              A pan-African cybersecurity curriculum built by BLVCK One
              and delivered inside the platform your team already uses.
            </p>

          </div>


          <div className="text-right">

            <div className="text-[10px] font-mono uppercase text-muted-foreground">
              ESG // Skills pledge
            </div>

            <div className="text-4xl font-display font-bold text-cyber tabular mt-1">
              10,000
            </div>

            <div className="text-xs text-muted-foreground">
              defenders trained by 2027
            </div>

          </div>

        </div>

      </div>



      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

        <StatCard
          label="Courses"
          value={String(COURSES.length)}
          tone="cyber"
          icon={BookOpen}
        />


        <StatCard
          label="Completed"
          value={String(
            COURSES.filter(
              (c) => c.progress === 100
            ).length
          )}
          tone="success"
          icon={Trophy}
        />


        <StatCard
          label="Certifications"
          value={String(
            BADGES.filter(
              (b) => b.earned
            ).length
          )}
          tone="warning"
          icon={Award}
        />


        <StatCard
          label="Team Enrolled"
          value="47 / 62"
          tone="cyber"
          icon={Users}
        />

      </div>



      <section>

        <div className="flex items-center justify-between mb-3">

          <h2 className="font-display text-xl font-bold">
            Course Catalog
          </h2>

          <button className="text-xs font-mono text-cyber">
            Browse all →
          </button>

        </div>


        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">

          {COURSES.map((course) => (

            <div
              key={course.title}
              className="glass p-5 flex flex-col gap-3"
            >

              <div className="flex justify-between">

                <span className="text-[10px] font-mono uppercase px-2 py-1 rounded border border-cyber/40 text-cyber">
                  {course.level}
                </span>


                <span className="text-[10px] font-mono text-muted-foreground">
                  {course.hours}h
                </span>

              </div>


              <h3 className="font-display font-bold text-lg">
                {course.title}
              </h3>


              <p className="text-xs text-muted-foreground">
                {course.enrolled.toLocaleString()} enrolled
                {" · "}
                <span className="text-cyber font-mono">
                  {course.cert}
                </span>
              </p>


              <div>

                <div className="flex justify-between text-[10px] font-mono mb-1">
                  <span>Progress</span>
                  <span>{course.progress}%</span>
                </div>


                <div className="h-1.5 bg-black/60 rounded overflow-hidden">

                  <div
                    className="h-full bg-cyber"
                    style={{
                      width: `${course.progress}%`,
                    }}
                  />

                </div>

              </div>


              <button className="bg-cyber text-black rounded-lg py-2 text-xs font-mono font-semibold flex items-center justify-center gap-2">

                <PlayCircle className="h-3.5 w-3.5" />

                {
                  course.progress === 0
                    ? "Start Course"
                    : course.progress === 100
                    ? "Review"
                    : "Continue"
                }

              </button>


            </div>

          ))}

        </div>

      </section>




      <section>

        <h2 className="font-display text-xl font-bold mb-3">
          Certification Badges
        </h2>


        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">

          {BADGES.map((badge)=>(

            <div
              key={badge.name}
              className={`glass p-4 text-center ${
                badge.earned ? "" : "opacity-40"
              }`}
            >

              <div
                className={`h-14 w-14 mx-auto rounded-full grid place-items-center ${
                  badge.earned
                    ? "bg-cyber/15 text-cyber ring-4 ring-cyber/20"
                    : "bg-white/5 text-muted-foreground"
                }`}
              >

                <GraduationCap className="h-6 w-6"/>

              </div>


              <div className="mt-3 text-xs font-mono">
                {badge.name}
              </div>


              <div className="text-[10px] mt-1 text-muted-foreground">
                {badge.earned ? "EARNED" : "LOCKED"}
              </div>


            </div>

          ))}

        </div>

      </section>


    </div>
  );
}