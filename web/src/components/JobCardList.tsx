"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { JobDetailsSheet } from "@/components/JobDetailsSheet";
import { Job, updateJob } from "@/lib/api";

interface JobCardListProps {
  jobs: Job[];
  onRefresh?: () => void;
}

const STAGE_OPTIONS = [
  "Backlog",
  "Applied",
  "Interviewing",
  "Offer",
  "Rejected",
  "Archived",
] as const;

const STAGE_COLORS: Record<string, string> = {
  Backlog: "bg-neutral-100 text-neutral-600",
  Applied: "bg-blue-50 text-blue-700",
  Interviewing: "bg-amber-50 text-amber-700",
  Offer: "bg-emerald-50 text-emerald-700",
  Rejected: "bg-red-50 text-red-600",
  Archived: "bg-neutral-100 text-neutral-500",
};

export function JobCardList({ jobs, onRefresh }: JobCardListProps) {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [updating, setUpdating] = useState<number | null>(null);

  const handleStageChange = async (job: Job, newStage: string) => {
    if (newStage === job.stage) return;
    setUpdating(job.id);
    try {
      await updateJob(job.id, { stage: newStage });
      onRefresh?.();
    } catch (err) {
      console.error("Failed to update stage:", err);
    } finally {
      setUpdating(null);
    }
  };

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
          <div
            key={job.id}
            onClick={() => setSelectedJob(job)}
            className={cn(
              "w-full rounded-lg border bg-white px-4 py-3 text-left transition-colors active:bg-neutral-50 cursor-pointer",
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
              <div
                onClick={(e) => e.stopPropagation()}
                className="shrink-0 ml-auto"
              >
                <Select
                  value={job.stage}
                  onValueChange={(v) => handleStageChange(job, v)}
                  disabled={updating === job.id}
                >
                  <SelectTrigger
                    className={cn(
                      "h-6 gap-1 rounded-full border-0 px-2.5 text-[10px] font-medium shadow-none",
                      STAGE_COLORS[job.stage] ?? STAGE_COLORS.Backlog
                    )}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STAGE_OPTIONS.map((stage) => (
                      <SelectItem key={stage} value={stage}>
                        {stage}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        ))}
      </div>
      <JobDetailsSheet
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        onRefresh={onRefresh}
      />
    </>
  );
}
