import { NextRequest, NextResponse } from "next/server";
import { getBackendHeaders } from "@/lib/api-headers";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const queryString = searchParams.toString();
  const url = `${BACKEND_URL}/api/jobs${queryString ? `?${queryString}` : ""}`;

  const headers = await getBackendHeaders();
  const response = await fetch(url, { headers });
  const data = await response.json();

  return NextResponse.json(data, { status: response.status });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const headers = await getBackendHeaders(true);

  const response = await fetch(`${BACKEND_URL}/api/jobs`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
