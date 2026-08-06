import MobileModule from "@/components/dashboard/mobile/module";

export const metadata = {
  title: "Mobile & PWA — BLVCK CYBER",
  description:
    "Install BLVCK CYBER on your phone — live alerts, security score, incident approvals and AI chat on the go.",
  openGraph: {
    title: "Mobile PWA — BLVCK CYBER",
    description:
      "SOC in your pocket. Approve incidents, chat with the AI analyst, monitor security posture.",
  },
};


export default function MobilePage() {
  return (
    <main className="space-y-6">
      <MobileModule />
    </main>
  );
}