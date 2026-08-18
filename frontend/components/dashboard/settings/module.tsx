"use client"

import { useState } from "react"

import {
  Bell,
  KeyRound,
  LockKeyhole,
  Save,
  Settings2,
  Shield,
  Webhook,
  Users,
  Database,
  Fingerprint,
  Activity,
} from "lucide-react"

import { toast } from "sonner"

import { PageHeader, Panel } from "@/components/dashboard/shared/ui"

import { Button } from "@/components/ui/button"

import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"

import { Input } from "@/components/ui/input"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import { Switch } from "@/components/ui/switch"

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"

import { Badge } from "@/components/ui/badge"



function ToggleRow({
  title,
  description,
  defaultChecked = false,
}: {
  title: string
  description: string
  defaultChecked?: boolean
}) {

  return (
    <div className="flex items-center justify-between rounded-lg border bg-muted/20 p-4">

      <div>
        <p className="text-sm font-medium">
          {title}
        </p>

        <p className="mt-1 text-xs text-muted-foreground">
          {description}
        </p>
      </div>


      <Switch
        defaultChecked={defaultChecked}
      />

    </div>
  )
}





export function SettingsModule() {


  const [section,setSection] =
    useState("Identity & Access")



  const save =
    () =>
      toast.success(
        "Settings saved. Changes recorded in audit log."
      )



  return (

<div className="flex flex-col gap-6">


<PageHeader

eyebrow="Tenant Administration"

title="Security Settings"

description="Manage identity, access control, integrations, security policies and platform behaviour."

actions={

<Button onClick={save}>

<Save className="mr-2 h-4 w-4"/>

Save Changes

</Button>

}

/>



<div className="grid gap-6 lg:grid-cols-[260px_1fr]">



<nav className="space-y-2">


{[

["Identity & Access",Shield],

["Platform",Settings2],

["Security",LockKeyhole],

["Data Governance",Database],

].map(([name,Icon])=>{


const Label=name as string

const IconComponent=Icon as any


return (

<Button

key={Label}

variant={
section===Label
?"secondary"
:"ghost"
}

className="w-full justify-start gap-3"

onClick={()=>
setSection(Label)
}

>

<IconComponent className="h-4 w-4"/>

{Label}

</Button>

)

})}


</nav>





<div className="space-y-6">





{
section==="Identity & Access" &&

<Panel

title="Identity & Access"

description="Authentication, users, roles and tenant permissions."

>


<Tabs defaultValue="authentication">


<TabsList>

<TabsTrigger value="authentication">
Authentication
</TabsTrigger>

<TabsTrigger value="roles">
RBAC
</TabsTrigger>

<TabsTrigger value="users">
Users
</TabsTrigger>

</TabsList>





<TabsContent
value="authentication"
className="space-y-4 pt-5"
>


<ToggleRow

title="Require MFA"

description="Require multi-factor authentication for privileged users."

defaultChecked

/>



<ToggleRow

title="Passkey Authentication"

description="Allow FIDO2 hardware keys and passwordless authentication."

/>



<FieldGroup>

<Field>

<FieldLabel>
Session Duration
</FieldLabel>


<Select defaultValue="8">

<SelectTrigger>

<SelectValue/>

</SelectTrigger>


<SelectContent>

<SelectItem value="4">
4 Hours
</SelectItem>

<SelectItem value="8">
8 Hours
</SelectItem>


<SelectItem value="12">
12 Hours
</SelectItem>


</SelectContent>


</Select>


<FieldDescription>

Sessions are automatically revoked after expiry.

</FieldDescription>


</Field>

</FieldGroup>


</TabsContent>







<TabsContent
value="roles"
className="space-y-3 pt-5"
>


{

[

["OWNER","Full tenant control"],

["ADMIN","User and configuration management"],

["SOC_MANAGER","SOC operations management"],

["SOC_ANALYST","Threat monitoring access"],

["INCIDENT_RESPONDER","Incident handling permissions"],

["VIEWER","Read-only access"],


].map(([role,desc])=>(


<div

key={role}

className="flex items-center justify-between rounded-lg border p-4"

>


<div>

<p className="font-medium">
{role}
</p>

<p className="text-xs text-muted-foreground">
{desc}
</p>

</div>


<Badge>
Active
</Badge>


</div>


))

}


</TabsContent>





<TabsContent

value="users"

className="pt-5"

>


<div className="rounded-lg border p-5">


<div className="flex items-center gap-3">

<Users className="h-5 w-5 text-primary"/>


<div>

<p className="font-medium">
Tenant Users
</p>


<p className="text-xs text-muted-foreground">

Manage users through Keycloak synchronization.

</p>

</div>


</div>


</div>


</TabsContent>


</Tabs>


</Panel>


}








{
section==="Platform" &&


<Panel

title="Platform Services"

description="API keys, webhooks and integrations."

>


<Tabs defaultValue="keys">


<TabsList>

<TabsTrigger value="keys">
API Keys
</TabsTrigger>


<TabsTrigger value="webhooks">
Webhooks
</TabsTrigger>


</TabsList>





<TabsContent value="keys" className="space-y-4 pt-5">


<div className="flex justify-between rounded-lg border p-4">


<div>

<p className="font-medium">
SOC Automation API
</p>

<p className="font-mono text-xs text-muted-foreground">
bc_live_••••92af
</p>


</div>


<Badge>
Active
</Badge>


</div>



<Button

onClick={()=>
toast.success("API key generated")
}

>

<KeyRound className="mr-2 h-4 w-4"/>

Generate API Key

</Button>


</TabsContent>







<TabsContent

value="webhooks"

className="space-y-4 pt-5"

>


<FieldGroup>


<Field>

<FieldLabel>
Webhook URL
</FieldLabel>


<Input

defaultValue="https://tenant.example.com/webhook"

/>


</Field>



<ToggleRow

title="Sign webhook payloads"

description="Protect events using HMAC signatures."

defaultChecked

/>



<Button variant="outline">


<Webhook className="mr-2 h-4 w-4"/>

Send Test Event


</Button>



</FieldGroup>


</TabsContent>


</Tabs>


</Panel>


}







{
section==="Security" &&


<Panel

title="Security Controls"

description="Threat protection and monitoring settings."

>


<div className="space-y-4">


<ToggleRow

title="Adaptive Risk Detection"

description="Detect unusual login behaviour."

defaultChecked

/>



<ToggleRow

title="Security Notifications"

description="Notify SOC teams about critical events."

defaultChecked

/>



<ToggleRow

title="Audit Logging"

description="Record administrator actions."

defaultChecked

/>


</div>


</Panel>


}







{
section==="Data Governance" &&


<Panel

title="Data Governance"

description="Retention and compliance settings."

>


<FieldGroup>


<Field>

<FieldLabel>
Event Retention
</FieldLabel>


<Select defaultValue="365">


<SelectTrigger>

<SelectValue/>

</SelectTrigger>


<SelectContent>

<SelectItem value="90">
90 Days
</SelectItem>


<SelectItem value="365">
365 Days
</SelectItem>


<SelectItem value="730">
730 Days
</SelectItem>


</SelectContent>


</Select>


</Field>


</FieldGroup>


</Panel>


}




</div>


</div>


</div>

  )
}