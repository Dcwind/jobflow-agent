"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createJobs, JobCreateResponse } from "@/lib/api";

interface JobFormProps {
  onSuccess: () => void;
}

export function JobForm({ onSuccess }: JobFormProps) {
  const [urls, setUrls] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<JobCreateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    // Parse URLs (one per line, filter empty)
    const urlList = urls
      .split("\n")
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    if (urlList.length === 0) {
      setError("Please enter at least one URL");
      return;
    }

    // Basic URL validation
    const invalidUrls = urlList.filter((u) => {
      try {
        new URL(u);
        return false;
      } catch {
        return true;
      }
    });

    if (invalidUrls.length > 0) {
      setError(`Invalid URLs: ${invalidUrls.join(", ")}`);
      return;
    }

    setLoading(true);
    try {
      const response = await createJobs(urlList);
      setResult(response);
      if (response.succeeded > 0) {
        setUrls("");
        onSuccess();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create jobs");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add Job URLs</CardTitle>
        <CardDescription>
          Enter one or more job posting URLs (one per line)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Textarea
            placeholder="https://example.com/jobs/software-engineer&#10;https://example.com/jobs/product-manager"
            value={urls}
            onChange={(e) => setUrls(e.target.value)}
            rows={5}
            disabled={loading}
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Extract Jobs"}
          </Button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 p-3 bg-gray-50 border rounded-md text-sm">
            <p>
              <strong>Results:</strong> {result.succeeded} succeeded,{" "}
              {result.failed} failed
            </p>
            {result.results
              .filter((r) => !r.success)
              .map((r, i) => (
                <p key={i} className="text-red-600 mt-1">
                  {r.url}: {r.error}
                </p>
              ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
