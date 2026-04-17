"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { JobDetailsSheet } from "@/components/JobDetailsSheet";
import { Job, updateJob, flagJob, deleteJob } from "@/lib/api";
import { Flag, Trash2 } from "lucide-react";

interface JobsTableProps {
  jobs: Job[];
  onRefresh: () => void;
}

interface EditingState {
  id: number;
  field: "title" | "company" | "location" | "salary";
  value: string;
}

const STAGE_OPTIONS = [
  "Backlog",
  "Applied",
  "Interviewing",
  "Offer",
  "Rejected",
  "Archived",
] as const;

export function JobsTable({ jobs, onRefresh }: JobsTableProps) {
  const [editing, setEditing] = useState<EditingState | null>(null);
  const [loading, setLoading] = useState<number | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const handleEdit = (
    job: Job,
    field: "title" | "company" | "location" | "salary"
  ) => {
    setEditing({
      id: job.id,
      field,
      value: (job[field] as string) || "",
    });
  };

  const handleSave = async () => {
    if (!editing) return;
    setLoading(editing.id);
    try {
      await updateJob(editing.id, { [editing.field]: editing.value });
      setEditing(null);
      onRefresh();
    } catch (err) {
      console.error("Failed to update:", err);
    } finally {
      setLoading(null);
    }
  };

  const handleCancel = () => {
    setEditing(null);
  };

  const handleStageChange = async (job: Job, newStage: string) => {
    setLoading(job.id);
    try {
      await updateJob(job.id, { stage: newStage });
      onRefresh();
    } catch (err) {
      console.error("Failed to update stage:", err);
    } finally {
      setLoading(null);
    }
  };

  const handleFlag = async (job: Job) => {
    setLoading(job.id);
    try {
      await flagJob(job.id, !job.flagged);
      onRefresh();
    } catch (err) {
      console.error("Failed to flag:", err);
    } finally {
      setLoading(null);
    }
  };

  const handleDelete = async (job: Job) => {
    if (!confirm(`Delete "${job.title}" at ${job.company}?`)) return;
    setLoading(job.id);
    try {
      await deleteJob(job.id);
      onRefresh();
    } catch (err) {
      console.error("Failed to delete:", err);
    } finally {
      setLoading(null);
    }
  };

  const renderCell = (
    job: Job,
    field: "title" | "company" | "location" | "salary"
  ) => {
    if (editing?.id === job.id && editing.field === field) {
      return (
        <div className="flex gap-1">
          <Input
            value={editing.value}
            onChange={(e) => setEditing({ ...editing, value: e.target.value })}
            className="h-7 text-sm"
            autoFocus
          />
          <Button size="sm" variant="outline" onClick={handleSave}>
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      );
    }
    return (
      <span
        className="cursor-pointer hover:bg-gray-100 px-1 rounded"
        onClick={() => handleEdit(job, field)}
        title="Click to edit"
      >
        {job[field] || "-"}
      </span>
    );
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
      <div className="rounded-md border overflow-x-auto scroll-padding-fix">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Salary</TableHead>
              <TableHead>Stage</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => (
              <TableRow
                key={job.id}
                className={job.flagged ? "bg-yellow-50" : ""}
              >
                <TableCell className="font-medium">
                  {renderCell(job, "title")}
                </TableCell>
                <TableCell>{renderCell(job, "company")}</TableCell>
                <TableCell>{renderCell(job, "location")}</TableCell>
                <TableCell>{renderCell(job, "salary")}</TableCell>
                <TableCell>
                  <Select
                    value={job.stage}
                    onValueChange={(value) => handleStageChange(job, value)}
                    disabled={loading === job.id}
                  >
                    <SelectTrigger className="h-8 w-[130px] text-xs">
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
                </TableCell>
                <TableCell>
                  <div className="flex gap-1 flex-nowrap items-center justify-end">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setSelectedJob(job)}
                      disabled={!job.description}
                    >
                      Details
                    </Button>
                    <Button
                      size="icon-sm"
                      variant="ghost"
                      className={
                        job.flagged
                          ? "text-amber-600 hover:text-amber-700 hover:bg-amber-50"
                          : "text-neutral-400 hover:text-amber-600 hover:bg-amber-50"
                      }
                      onClick={() => handleFlag(job)}
                      disabled={loading === job.id}
                      title={job.flagged ? "Clear flag" : "Flag issue"}
                      aria-label={job.flagged ? "Clear flag" : "Flag issue"}
                    >
                      <Flag
                        className="h-4 w-4"
                        fill={job.flagged ? "currentColor" : "none"}
                      />
                    </Button>
                    <Button
                      size="icon-sm"
                      variant="ghost"
                      className="text-neutral-400 hover:text-red-600 hover:bg-red-50"
                      onClick={() => handleDelete(job)}
                      disabled={loading === job.id}
                      title="Delete"
                      aria-label="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <JobDetailsSheet
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
      />
    </>
  );
}
