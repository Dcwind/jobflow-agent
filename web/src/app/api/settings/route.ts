import { NextRequest, NextResponse } from "next/server";
import { getBackendHeaders } from "@/lib/api-headers";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET() {
  const headers = await getBackendHeaders();
  const response = await fetch(`${BACKEND_URL}/api/settings`, { headers });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function PUT(request: NextRequest) {
  const body = await request.json();
  const headers = await getBackendHeaders(true);
  const response = await fetch(`${BACKEND_URL}/api/settings`, {
    method: "PUT",
    headers,
    body: JSON.stringify(body),
  });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
