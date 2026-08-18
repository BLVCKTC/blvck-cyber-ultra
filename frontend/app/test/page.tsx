import { generatePKCE } from "@/lib/auth/pkce";

export default function TestPage() {
  const pkce = generatePKCE();

  console.log(pkce);

  return (
    <pre>{JSON.stringify(pkce, null, 2)}</pre>
  );
}