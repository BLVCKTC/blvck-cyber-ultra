import InsuranceModule from "@/components/dashboard/insurance/module";

export const metadata = {
  title: "Cyber Insurance — BLVCK CYBER",
  description:
    "Bundle cyber insurance priced against your live BLVCK CYBER security posture score.",
  openGraph: {
    title: "Cyber Insurance — BLVCK CYBER",
    description:
      "Turn a strong posture into a lower premium — partner-underwritten cyber cover.",
  },
};


export default function InsurancePage() {
  return (
    <main className="space-y-6">
      <InsuranceModule />
    </main>
  );
}