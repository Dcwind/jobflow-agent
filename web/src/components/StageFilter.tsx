"use client";

import { cn } from "@/lib/utils";

export const STAGE_FILTER_OPTIONS = [
  "Backlog",
  "Applied",
  "Interviewing",
  "Offer",
  "Rejected",
  "Archived",
] as const;

export type StageFilter = (typeof STAGE_FILTER_OPTIONS)[number] | null;

interface StageFilterBarProps {
  value: StageFilter;
  onChange: (next: StageFilter) => void;
  counts?: Record<string, number>;
}

export function StageFilterBar({
  value,
  onChange,
  counts = {},
}: StageFilterBarProps) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <Chip active={value === null} onClick={() => onChange(null)} count={total}>
        All
      </Chip>
      {STAGE_FILTER_OPTIONS.map((stage) => (
        <Chip
          key={stage}
          active={value === stage}
          onClick={() => onChange(stage)}
          count={counts[stage] ?? 0}
        >
          {stage}
        </Chip>
      ))}
    </div>
  );
}

function Chip({
  active,
  onClick,
  children,
  count,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  count?: number;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors",
        active
          ? "border-neutral-900 bg-neutral-900 text-white"
          : "border-neutral-200 bg-white text-neutral-600 hover:border-neutral-400 hover:text-neutral-900"
      )}
    >
      <span>{children}</span>
      {count !== undefined && (
        <span
          className={cn(
            "tabular-nums",
            active ? "text-white/70" : "text-neutral-400"
          )}
        >
          {count}
        </span>
      )}
    </button>
  );
}
