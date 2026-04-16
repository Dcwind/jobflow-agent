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
}

export function StageFilterBar({ value, onChange }: StageFilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <Chip active={value === null} onClick={() => onChange(null)}>
        All
      </Chip>
      {STAGE_FILTER_OPTIONS.map((stage) => (
        <Chip
          key={stage}
          active={value === stage}
          onClick={() => onChange(stage)}
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
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
        active
          ? "border-neutral-900 bg-neutral-900 text-white"
          : "border-neutral-200 bg-white text-neutral-600 hover:border-neutral-400 hover:text-neutral-900"
      )}
    >
      {children}
    </button>
  );
}
