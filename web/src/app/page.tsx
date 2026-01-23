"use client";

import { useEffect, useState, useCallback } from "react";
import { JobForm } from "@/components/JobForm";
import { JobsTable } from "@/components/JobsTable";
import { ExportButton } from "@/components/ExportButton";
import { Button } from "@/components/ui/button";
import { listJobs, Job, JobListResponse } from "@/lib/api";

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pages: 1,
    total: 0,
  });

  const fetchJobs = useCallback(async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response: JobListResponse = await listJobs(page);
      setJobs(response.jobs);
      setPagination({
        page: response.page,
        pages: response.pages,
        total: response.total,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch jobs");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleRefresh = () => {
    fetchJobs(pagination.page);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto py-8 px-4">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Jobflow</h1>
          <p className="text-gray-600 mt-1">
            Extract and track job postings from any URL
          </p>
        </header>

        <div className="grid gap-6">
          <JobForm onSuccess={handleRefresh} />

          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              Saved Jobs {pagination.total > 0 && `(${pagination.total})`}
            </h2>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleRefresh} disabled={loading}>
                Refresh
              </Button>
              <ExportButton disabled={jobs.length === 0} />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}

          {loading && jobs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : (
            <JobsTable jobs={jobs} onRefresh={handleRefresh} />
          )}

          {pagination.pages > 1 && (
            <div className="flex justify-center gap-2">
              <Button
                variant="outline"
                onClick={() => fetchJobs(pagination.page - 1)}
                disabled={pagination.page <= 1 || loading}
              >
                Previous
              </Button>
              <span className="flex items-center px-4 text-sm text-gray-600">
                Page {pagination.page} of {pagination.pages}
              </span>
              <Button
                variant="outline"
                onClick={() => fetchJobs(pagination.page + 1)}
                disabled={pagination.page >= pagination.pages || loading}
              >
                Next
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
