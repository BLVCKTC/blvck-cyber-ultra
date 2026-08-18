"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { toast } from "sonner";
import {
  ArrowLeft,
  CheckCircle2,
  ShieldCheck,
} from "lucide-react";

import {ParticleField} from "@/components/particle-field";


const AFRICAN_COUNTRIES = [
  "Zimbabwe",
  "South Africa",
  "Botswana",
  "Zambia",
  "Mozambique",
  "Namibia",
  "Kenya",
  "Nigeria",
  "Ghana",
  "Egypt",
  "Ethiopia",
  "Tanzania",
  "Uganda",
  "Rwanda",
];

const INDUSTRIES = [
  "Banking & Finance",
  "Government",
  "Mining",
  "Telecommunications",
  "Healthcare",
  "Energy",
  "Manufacturing",
  "Retail",
  "Education",
  "Technology",
];


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



export default function DemoRequest() {

  const router = useRouter();


  const [state,setState] = useState({

    company:"",
    contact:"",
    email:"",
    phone:"",
    industry:"",
    size:"",
    country:"",
    challenges:[] as string[],
    demoDate:"",
    contactMethod:"Email",
    hp:"",

  });


  const [errors,setErrors] =
    useState<Record<string,string>>({});


  const [done,setDone] = useState(false);


  const [lastSubmit,setLastSubmit] =
    useState(0);



  const setField = <
    K extends keyof typeof state
  >(
    key:K,
    value:(typeof state)[K]
  ) => {

    setState(prev=>({
      ...prev,
      [key]:value
    }));

  };



  const toggleChallenge = (challenge:string)=>{

    setState(prev=>({

      ...prev,

      challenges:
        prev.challenges.includes(challenge)

        ? prev.challenges.filter(
            x=>x!==challenge
          )

        : [
            ...prev.challenges,
            challenge
          ]

    }));

  };



  const submit = (
    e:React.FormEvent<HTMLFormElement>
  )=>{

    e.preventDefault();


    if(Date.now()-lastSubmit < 5000){

      toast.error(
        "Please slow down."
      );

      return;
    }



    const parsed =
      schema.safeParse(state);



    if(!parsed.success){

      const errs:Record<string,string>={};


      parsed.error.issues.forEach(
        (issue)=>{

          errs[
            issue.path[0] as string
          ] = issue.message;

        }
      );


      setErrors(errs);


      toast.error(
        "Please fix the highlighted fields."
      );


      return;

    }



    if(parsed.data.hp)
      return;



    setLastSubmit(Date.now());
    setErrors({});
    setDone(true);


    toast.success(
      "Demo request received — we'll reach out within 4 hours."
    );

  };



  if(done){

    return (

      <div className="min-h-screen grid place-items-center px-4 relative overflow-hidden">

        <div className="absolute inset-0">

          <ParticleField />

        </div>


        <div className="relative glass-strong p-10 max-w-lg text-center">


          <CheckCircle2
            className="h-16 w-16 text-success mx-auto"
          />


          <h1 className="mt-6 text-3xl font-display font-bold">
            Request received
          </h1>


          <p className="mt-4 text-muted-foreground text-sm">

            A BLVCK CYBER solutions architect will contact{" "}

            <span className="text-cyber">
              {state.email}
            </span>

            within 4 business hours.

          </p>



          <div className="mt-8 flex gap-3 justify-center">


            <Link
              href="/"
              className="border border-cyber/40 text-cyber px-4 py-2 rounded-lg text-sm"
            >
              Home
            </Link>



            <button

              onClick={()=>
                router.push("/dashboard/soc-demo")
              }

              className="bg-cyber text-black font-semibold px-4 py-2 rounded-lg text-sm"

            >

              Try AI-SOC Simulator

            </button>


          </div>


        </div>


      </div>

    );

  }



  const input =
    "w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2.5 text-sm";



  return (

    <div className="min-h-screen relative">


      <div className="absolute inset-0 hud-grid opacity-30"/>


      <div className="relative max-w-4xl mx-auto p-6 lg:p-10">


        <Link

          href="/"

          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-cyber mb-6"

        >

          <ArrowLeft className="h-4 w-4"/>

          Back to home

        </Link>



        <div className="glass-strong p-8">


          <div className="flex items-center gap-2 text-xs font-mono text-cyber">

            <ShieldCheck className="h-4 w-4"/>

            SECURE DEMO REQUEST

          </div>



          <h1 className="mt-3 text-4xl font-bold">

            See BLVCK CYBER in your environment.

          </h1>



          <form
            onSubmit={submit}
            className="mt-8 grid md:grid-cols-2 gap-4"
          >


            <input
              className="hidden"
              name="hp"
              value={state.hp}
              onChange={
                e=>setField("hp",e.target.value)
              }
            />



            {[
              ["company","Company name"],
              ["contact","Contact person"],
              ["email","Business email"],
              ["phone","Phone"],
            ].map(([key,label])=>(

              <Field
                key={key}
                label={label}
              >

                <input

                  className={input}

                  value={
                    state[
                      key as keyof typeof state
                    ] as string
                  }

                  onChange={
                    e=>setField(
                      key as keyof typeof state,
                      e.target.value as never
                    )
                  }

                />

              </Field>

            ))}



            <Field label="Industry">

              <select
                className={input}
                value={state.industry}
                onChange={
                  e=>setField(
                    "industry",
                    e.target.value
                  )
                }
              >

                <option value="">
                  Select
                </option>

                {INDUSTRIES.map(
                  (industry:string)=>(

                    <option key={industry}>
                      {industry}
                    </option>

                  )
                )}

              </select>

            </Field>



            <Field label="Country">

              <select
                className={input}
                value={state.country}
                onChange={
                  e=>setField(
                    "country",
                    e.target.value
                  )
                }
              >

                <option value="">
                  Select
                </option>

                {AFRICAN_COUNTRIES.map(
                  (country:string)=>(

                    <option key={country}>
                      {country}
                    </option>

                  )
                )}

              </select>

            </Field>



            <div className="md:col-span-2">


              <label className="text-xs">
                Security challenges
              </label>


              <div className="flex flex-wrap gap-2 mt-3">

                {CHALLENGES.map(
                  (challenge:string)=>(

                    <button

                      key={challenge}

                      type="button"

                      onClick={()=>
                        toggleChallenge(challenge)
                      }

                      className="border px-3 py-1 rounded-lg text-xs"

                    >

                      {challenge}

                    </button>

                  )
                )}

              </div>


            </div>



            <Field label="Preferred date">

              <input

                type="date"

                className={input}

                value={state.demoDate}

                onChange={
                  e=>setField(
                    "demoDate",
                    e.target.value
                  )
                }

              />

            </Field>



            <button

              type="submit"

              className="md:col-span-2 bg-cyber text-black py-3 rounded-lg font-semibold"

            >

              Request demo

            </button>



          </form>


        </div>


      </div>


    </div>

  );

}




function Field(
{
 label,
 children
}:{
 label:string;
 children:React.ReactNode;
}
){

return (

<div>

<label className="text-xs font-mono uppercase">

{label}

</label>


<div className="mt-2">

{children}

</div>


</div>

);

}