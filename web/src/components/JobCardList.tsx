"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { JobDetailsSheet } from "@/components/JobDetailsSheet";
import { Job } from "@/lib/api";

interface JobCardListProps {
  jobs: Job[];
  onRefresh?: () => void;
}

const STAGE_COLORS: Record<string, string> = {
  Backlog: "bg-neutral-100 text-neutral-600",
  Applied: "bg-blue-50 text-blue-700",
  Interviewing: "bg-amber-50 text-amber-700",
  Offer: "bg-emerald-50 text-emerald-700",
  Rejected: "bg-red-50 text-red-600",
  Archived: "bg-neutral-100 text-neutral-500",
};

export function JobCardList({ jobs }: JobCardListProps) {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  if (jobs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No jobs yet. Add some URLs above to get started.
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col gap-2">
        {jobs.map((job) => (
          <button
            key={job.id}
            type="button"
            onClick={() => setSelectedJob(job)}
            className={cn(
              "w-full rounded-lg border bg-white px-4 py-3 text-left transition-colors active:bg-neutral-50",
              job.flagged && "border-l-2 border-l-amber-400"
            )}
          >
            <p className="text-sm font-medium leading-snug text-neutral-900 line-clamp-2">
              {job.title}
            </p>
            <div className="mt-1.5 flex items-center gap-2">
              <span className="text-xs text-neutral-500 truncate">
                {job.company}
              </span>
              <span
                className={cn(
                  "shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium",
                  STAGE_COLORS[job.stage] ?? STAGE_COLORS.Backlog
                )}
              >
                {job.stage}
              </span>
            </div>
          </button>
        ))}
      </div>
      <JobDetailsSheet
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
      />
    </>
  );
}
