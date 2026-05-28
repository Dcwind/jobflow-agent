"use client";

import { signIn } from "@/lib/auth-client";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo } from "react";

function validateParams(searchParams: URLSearchParams) {
  const provider = searchParams.get("provider");
  const redirectUri = searchParams.get("redirect_uri");

  if (!provider || !redirectUri) {
    return { error: "Missing provider or redirect_uri" };
  }

  try {
    const url = new URL(redirectUri);
    if (!url.hostname.endsWith(".chromiumapp.org")) {
      return { error: "Invalid redirect URI" };
    }
  } catch {
    return { error: "Invalid redirect URI" };
  }

  return { provider: provider as "google" | "github", redirectUri };
}

export default function ExtensionSignInPage() {
  const searchParams = useSearchParams();
  const params = useMemo(() => validateParams(searchParams), [searchParams]);

  useEffect(() => {
    if ("error" in params) return;

    const callbackURL =
      "/api/auth/extension-token?redirect_uri=" +
      encodeURIComponent(params.redirectUri);

    signIn.social({
      provider: params.provider,
      callbackURL,
    });
  }, [params]);

  if ("error" in params) {
    return (
      <div style={{ padding: 40, textAlign: "center", fontFamily: "system-ui" }}>
        <p>{params.error}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 40, textAlign: "center", fontFamily: "system-ui" }}>
      <p>Signing you in...</p>
    </div>
  );
}
