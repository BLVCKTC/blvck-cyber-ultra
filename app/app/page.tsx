import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/api/auth";

export default async function AppRouterPage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  switch (user.role) {
    case "admin":
      redirect("/admin");

    default:
      redirect(`/dashboard/${user.tenantId}`);
  }
}