import crypto from "crypto";

/**
 * Generate a high-entropy PKCE code verifier.
 */
export function generateCodeVerifier(): string {
  return crypto.randomBytes(32).toString("base64url");
}

/**
 * Generate a SHA256 PKCE code challenge.
 */
export function generateCodeChallenge(verifier: string): string {
  return crypto
    .createHash("sha256")
    .update(verifier)
    .digest("base64url");
}

/**
 * Generate both values together.
 */
export function generatePKCE() {
  const verifier = generateCodeVerifier();
  const challenge = generateCodeChallenge(verifier);

  return {
    verifier,
    challenge,
    challengeMethod: "S256",
  };
}