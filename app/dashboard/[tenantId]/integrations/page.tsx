import IntegrationsModule from "@/components/dashboard/integrations/module";

export const metadata = {
  title: "Integrations Marketplace — BLVCK CYBER",
  description:
    "Connect Microsoft 365, Google Workspace, AWS, Azure, GCP, EDR, SIEM, ITSM and ChatOps to BLVCK CYBER.",
  openGraph: {
    title: "Integrations Marketplace — BLVCK CYBER",
    description:
      "One-click integrations across cloud, identity, endpoint, SIEM and collaboration.",
  },
};


export default function IntegrationsPage() {
  return (
    <main className="space-y-6">
      <IntegrationsModule />
    </main>
  );
}