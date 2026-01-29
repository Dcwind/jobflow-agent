import { headers } from "next/headers";
import { auth } from "./auth";

const API_KEY = process.env.API_KEY;

/**
 * Build headers for backend API requests.
 * Includes API key and forwards user session token if authenticated.
 */
export async function getBackendHeaders(
  includeContentType = false
): Promise<HeadersInit> {
  const result: HeadersInit = {};

  // Add API key for server-to-server auth
  if (API_KEY) {
    result["X-API-Key"] = API_KEY;
  }

  // Get session from Better Auth cookies
  const requestHeaders = await headers();
  const session = await auth.api.getSession({ headers: requestHeaders });

  // Forward session token for user auth
  if (session?.session?.token) {
    result["Authorization"] = `Bearer ${session.session.token}`;
  }

  if (includeContentType) {
    result["Content-Type"] = "application/json";
  }

  return result;
}
