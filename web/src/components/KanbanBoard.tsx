"use client";

import { useState } from "react";
import {
  DndContext,
  DragOverlay,
  useDraggable,
  useDroppable,
  closestCenter,
  type DragStartEvent,
  type DragEndEvent,
} from "@dnd-kit/core";
import { cn } from "@/lib/utils";
import { JobDetailsSheet } from "@/components/JobDetailsSheet";
import { Job, updateJob } from "@/lib/api";

const STAGES = [
  "Backlog",
  "Applied",
  "Interviewing",
  "Offer",
  "Rejected",
  "Archived",
] as const;

interface KanbanBoardProps {
  jobs: Job[];
  onRefresh: () => void;
}

export function KanbanBoard({ jobs, onRefresh }: KanbanBoardProps) {
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [updating, setUpdating] = useState<number | null>(null);

  const grouped = new Map<string, Job[]>();
  for (const stage of STAGES) grouped.set(stage, []);
  for (const job of jobs) {
    const list = grouped.get(job.stage);
    if (list) list.push(job);
    else grouped.get("Backlog")!.push(job);
  }

  const handleDragStart = (event: DragStartEvent) => {
    const job = jobs.find((j) => j.id === event.active.id);
    if (job) setActiveJob(job);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    setActiveJob(null);
    const { active, over } = event;
    if (!over) return;

    const jobId = active.id as number;
    const newStage = over.id as string;
    const job = jobs.find((j) => j.id === jobId);
    if (!job || job.stage === newStage) return;

    setUpdating(jobId);
    try {
      await updateJob(jobId, { stage: newStage });
      onRefresh();
    } catch (err) {
      console.error("Failed to move job:", err);
    } finally {
      setUpdating(null);
    }
  };

  return (
    <>
      <DndContext
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STAGES.map((stage) => {
            const stageJobs = grouped.get(stage) ?? [];
            return (
              <Column key={stage} stage={stage} count={stageJobs.length}>
                {stageJobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    updating={updating === job.id}
                    onClick={() => setSelectedJob(job)}
                  />
                ))}
              </Column>
            );
          })}
        </div>

        <DragOverlay>
          {activeJob && <CardContent job={activeJob} overlay />}
        </DragOverlay>
      </DndContext>

      <JobDetailsSheet
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
      />
    </>
  );
}

function Column({
  stage,
  count,
  children,
}: {
  stage: string;
  count: number;
  children: React.ReactNode;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: stage });

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "flex w-[260px] flex-shrink-0 flex-col rounded-lg border bg-neutral-50/80 transition-colors",
        isOver && "border-neutral-400 bg-neutral-100"
      )}
    >
      <div className="flex items-center justify-between px-3 py-2.5 border-b border-neutral-200/60">
        <span className="text-xs font-semibold tracking-wide text-neutral-700">
          {stage}
        </span>
        <span className="text-[10px] tabular-nums font-medium text-neutral-400">
          {count}
        </span>
      </div>
      <div className="flex flex-col gap-2 p-2 min-h-[80px]">{children}</div>
    </div>
  );
}

function JobCard({
  job,
  updating,
  onClick,
}: {
  job: Job;
  updating: boolean;
  onClick: () => void;
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id: job.id });

  const style = transform
    ? { transform: `translate(${transform.x}px, ${transform.y}px)` }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      style={style}
      onClick={onClick}
      className={cn(
        "cursor-grab active:cursor-grabbing",
        isDragging && "opacity-30",
        updating && "opacity-50 pointer-events-none"
      )}
    >
      <CardContent job={job} />
    </div>
  );
}

function CardContent({ job, overlay }: { job: Job; overlay?: boolean }) {
  return (
    <div
      className={cn(
        "rounded-md border bg-white px-3 py-2.5 shadow-sm transition-shadow",
        overlay && "shadow-lg ring-1 ring-neutral-200",
        job.flagged && "border-l-2 border-l-amber-400"
      )}
    >
      <p className="text-sm font-medium leading-snug text-neutral-900 line-clamp-2">
        {job.title}
      </p>
      <p className="mt-0.5 text-xs text-neutral-500 truncate">{job.company}</p>
      {job.location && (
        <p className="mt-0.5 text-[11px] text-neutral-400 truncate">
          {job.location}
        </p>
      )}
    </div>
  );
}
