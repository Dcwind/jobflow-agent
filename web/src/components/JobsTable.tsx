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
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Job, updateJob, flagJob, deleteJob } from "@/lib/api";

interface JobsTableProps {
  jobs: Job[];
  onRefresh: () => void;
}

interface EditingState {
  id: number;
  field: "title" | "company" | "location" | "salary";
  value: string;
}

export function JobsTable({ jobs, onRefresh }: JobsTableProps) {
  const [editing, setEditing] = useState<EditingState | null>(null);
  const [loading, setLoading] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

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
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Company</TableHead>
            <TableHead>Location</TableHead>
            <TableHead>Salary</TableHead>
            <TableHead>Source</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.map((job) => (
            <>
              <TableRow key={job.id} className={job.flagged ? "bg-yellow-50" : ""}>
                <TableCell className="font-medium">
                  {renderCell(job, "title")}
                </TableCell>
                <TableCell>{renderCell(job, "company")}</TableCell>
                <TableCell>{renderCell(job, "location")}</TableCell>
                <TableCell>{renderCell(job, "salary")}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="text-xs">
                    {job.extraction_method || "unknown"}
                  </Badge>
                </TableCell>
                <TableCell>
                  {job.flagged && (
                    <Badge variant="destructive" className="text-xs">
                      Flagged
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    {job.description && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setExpandedId(expandedId === job.id ? null : job.id)}
                      >
                        {expandedId === job.id ? "Hide" : "Details"}
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleFlag(job)}
                      disabled={loading === job.id}
                      title={job.flagged ? "Unflag" : "Flag for review"}
                    >
                      {job.flagged ? "Unflag" : "Flag"}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => handleDelete(job)}
                      disabled={loading === job.id}
                    >
                      Delete
                    </Button>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm px-2 py-1"
                    >
                      View
                    </a>
                  </div>
                </TableCell>
              </TableRow>
              {expandedId === job.id && job.description && (
                <TableRow key={`${job.id}-desc`} className="bg-gray-50">
                  <TableCell colSpan={7} className="py-4">
                    <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
                      {job.description}
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
