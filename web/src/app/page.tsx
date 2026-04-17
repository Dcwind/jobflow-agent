"use client";

import { useEffect, useState, useCallback } from "react";
import { JobForm } from "@/components/JobForm";
import { JobsTable } from "@/components/JobsTable";
import { JobCardList } from "@/components/JobCardList";
import { KanbanBoard } from "@/components/KanbanBoard";
import { ExportButton } from "@/components/ExportButton";
import { UserMenu } from "@/components/UserMenu";
import { StageFilterBar, StageFilter } from "@/components/StageFilter";
import { Sheet } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Plus, List, Kanban } from "lucide-react";
import { cn } from "@/lib/utils";
import { listJobs, Job, JobListResponse } from "@/lib/api";

type View = "table" | "board";

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<View>("table");
  const [stageFilter, setStageFilter] = useState<StageFilter>(null);
  const [stageCounts, setStageCounts] = useState<Record<string, number>>({});
  const [addOpen, setAddOpen] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    pages: 1,
    total: 0,
  });

  const fetchJobs = useCallback(
    async (
      page = 1,
      stage: StageFilter = null,
      perPage = 20
    ) => {
      setLoading(true);
      setError(null);
      try {
        const response: JobListResponse = await listJobs(
          page,
          perPage,
          stage ? { stage } : undefined
        );
        setJobs(response.jobs);
        setStageCounts(response.stage_counts ?? {});
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
    },
    []
  );

  const totalJobs = Object.values(stageCounts).reduce((a, b) => a + b, 0);
  const activeCount = stageCounts["Applied"] ?? 0;
  const interviewingCount = stageCounts["Interviewing"] ?? 0;
  const offerCount = stageCounts["Offer"] ?? 0;

  const isBoard = view === "board";
  const perPage = isBoard ? 100 : 20;

  useEffect(() => {
    fetchJobs(1, isBoard ? null : stageFilter, perPage);
  }, [fetchJobs, stageFilter, isBoard, perPage]);

  const handleRefresh = () => {
    fetchJobs(isBoard ? 1 : pagination.page, isBoard ? null : stageFilter, perPage);
  };

  const handleStageFilterChange = (next: StageFilter) => {
    setStageFilter(next);
  };

  const handleViewChange = (next: View) => {
    setView(next);
    if (next === "board") setStageFilter(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-7xl mx-auto py-8 px-4">
        <header className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Jobflow</h1>
            {totalJobs > 0 ? (
              <p className="mt-1 text-sm text-gray-600">
                <span className="font-medium text-gray-900">{totalJobs}</span>{" "}
                in pipeline
                <span className="mx-2 text-gray-300">·</span>
                <span className="font-medium text-gray-900">{activeCount}</span>{" "}
                applied
                <span className="mx-2 text-gray-300">·</span>
                <span className="font-medium text-gray-900">
                  {interviewingCount}
                </span>{" "}
                interviewing
                {offerCount > 0 && (
                  <>
                    <span className="mx-2 text-gray-300">·</span>
                    <span className="font-medium text-emerald-700">
                      {offerCount}
                    </span>{" "}
                    {offerCount === 1 ? "offer" : "offers"}
                  </>
                )}
              </p>
            ) : (
              <p className="mt-1 text-sm text-gray-600">
                Add a job URL to start tracking your pipeline.
              </p>
            )}
          </div>
          <UserMenu />
        </header>

        <div className="grid gap-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-xl font-semibold">
              Saved Jobs {pagination.total > 0 && `(${pagination.total})`}
            </h2>
            <div className="flex flex-wrap gap-2">
              <div className="flex rounded-md border bg-white">
                <button
                  onClick={() => handleViewChange("table")}
                  className={cn(
                    "flex items-center gap-1 rounded-l-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                    view === "table"
                      ? "bg-neutral-900 text-white"
                      : "text-neutral-500 hover:text-neutral-900"
                  )}
                >
                  <List className="h-3.5 w-3.5" />
                  Table
                </button>
                <button
                  onClick={() => handleViewChange("board")}
                  className={cn(
                    "flex items-center gap-1 rounded-r-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                    view === "board"
                      ? "bg-neutral-900 text-white"
                      : "text-neutral-500 hover:text-neutral-900"
                  )}
                >
                  <Kanban className="h-3.5 w-3.5" />
                  Board
                </button>
              </div>
              <Button variant="outline" size="sm" onClick={handleRefresh} disabled={loading}>
                Refresh
              </Button>
              <ExportButton disabled={jobs.length === 0} />
              <Button size="sm" onClick={() => setAddOpen(true)}>
                <Plus className="h-4 w-4" />
                Add jobs
              </Button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}

          {loading && jobs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : isBoard ? (
            <KanbanBoard jobs={jobs} onRefresh={handleRefresh} />
          ) : (
            <>
              <StageFilterBar
                value={stageFilter}
                onChange={handleStageFilterChange}
                counts={stageCounts}
              />
              <div className="hidden md:block">
                <JobsTable jobs={jobs} onRefresh={handleRefresh} />
              </div>
              <div className="md:hidden">
                <JobCardList jobs={jobs} onRefresh={handleRefresh} />
              </div>
              {pagination.pages > 1 && (
                <div className="flex justify-center gap-2">
                  <Button
                    variant="outline"
                    onClick={() => fetchJobs(pagination.page - 1, stageFilter, perPage)}
                    disabled={pagination.page <= 1 || loading}
                  >
                    Previous
                  </Button>
                  <span className="flex items-center px-4 text-sm text-gray-600">
                    Page {pagination.page} of {pagination.pages}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => fetchJobs(pagination.page + 1, stageFilter, perPage)}
                    disabled={pagination.page >= pagination.pages || loading}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <Sheet open={addOpen} onClose={() => setAddOpen(false)}>
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-neutral-200/70 px-4 py-4 sm:px-8">
            <div className="text-[11px] uppercase tracking-[0.18em] text-neutral-500">
              Add jobs
            </div>
            <button
              onClick={() => setAddOpen(false)}
              className="text-sm text-neutral-500 transition-colors hover:text-neutral-900"
              aria-label="Close"
            >
              Close ✕
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 sm:p-8">
            <JobForm
              onSuccess={() => {
                handleRefresh();
                setAddOpen(false);
              }}
            />
          </div>
        </div>
      </Sheet>
    </div>
  );
}
