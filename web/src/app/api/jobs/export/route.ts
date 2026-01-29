import { NextRequest, NextResponse } from "next/server";
import { getBackendHeaders } from "@/lib/api-headers";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const queryString = searchParams.toString();
  const url = `${BACKEND_URL}/api/jobs/export${queryString ? `?${queryString}` : ""}`;

  const headers = await getBackendHeaders();
  const response = await fetch(url, { headers });
  const csvContent = await response.text();

  return new NextResponse(csvContent, {
    status: response.status,
    headers: {
      "Content-Type": "text/csv",
      "Content-Disposition": "attachment; filename=jobs.csv",
    },
  });
}
