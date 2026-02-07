import { NextRequest, NextResponse } from "next/server";
import { getBackendHeaders } from "@/lib/api-headers";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

type RouteParams = { params: Promise<{ id: string }> };

export async function GET(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const headers = await getBackendHeaders();
  const response = await fetch(`${BACKEND_URL}/api/jobs/${id}`, { headers });
  const data = await response.json();

  return NextResponse.json(data, { status: response.status });
}

export async function PATCH(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const body = await request.json();
  const headers = await getBackendHeaders(true);

  const response = await fetch(`${BACKEND_URL}/api/jobs/${id}`, {
    method: "PATCH",
    headers,
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const headers = await getBackendHeaders();

  const response = await fetch(`${BACKEND_URL}/api/jobs/${id}`, {
    method: "DELETE",
    headers,
  });

  if (response.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
