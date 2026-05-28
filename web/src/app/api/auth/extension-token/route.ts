import { auth } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";
import { headers as nextHeaders } from "next/headers";

export async function GET(request: NextRequest) {
  const redirectUri = request.nextUrl.searchParams.get("redirect_uri");

  if (!redirectUri) {
    return NextResponse.json(
      { error: "Missing redirect_uri" },
      { status: 400 }
    );
  }

  // Validate redirect_uri — only allow chromiumapp.org
  try {
    const url = new URL(redirectUri);
    if (!url.hostname.endsWith(".chromiumapp.org")) {
      return NextResponse.json(
        { error: "Invalid redirect URI" },
        { status: 400 }
      );
    }
  } catch {
    return NextResponse.json(
      { error: "Invalid redirect URI" },
      { status: 400 }
    );
  }

  // Get the session from Better Auth using the cookie set during OAuth
  const session = await auth.api.getSession({
    headers: await nextHeaders(),
  });

  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  // Build redirect URL with token and user info
  const target = new URL(redirectUri);
  target.searchParams.set("token", session.session.token);
  if (session.user.email) {
    target.searchParams.set("email", session.user.email);
  }
  if (session.user.name) {
    target.searchParams.set("name", session.user.name);
  }

  return NextResponse.redirect(target.toString());
}
