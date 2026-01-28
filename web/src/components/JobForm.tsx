"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createJobs, createJobManual, parseJobDescription, JobCreateResponse } from "@/lib/api";

interface JobFormProps {
  onSuccess: () => void;
}

type FormMode = "url" | "manual";

interface ManualFormData {
  title: string;
  company: string;
  location: string;
  salary: string;
  description: string;
  url: string;
}

const emptyManualForm: ManualFormData = {
  title: "",
  company: "",
  location: "",
  salary: "",
  description: "",
  url: "",
};

export function JobForm({ onSuccess }: JobFormProps) {
  const [mode, setMode] = useState<FormMode>("url");
  const [urls, setUrls] = useState("");
  const [manualForm, setManualForm] = useState<ManualFormData>(emptyManualForm);
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [result, setResult] = useState<JobCreateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setSuccess(null);

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

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setSuccess(null);

    if (!manualForm.title.trim() || !manualForm.company.trim()) {
      setError("Title and Company are required");
      return;
    }

    setLoading(true);
    try {
      await createJobManual({
        title: manualForm.title.trim(),
        company: manualForm.company.trim(),
        location: manualForm.location.trim() || undefined,
        salary: manualForm.salary.trim() || undefined,
        description: manualForm.description.trim() || undefined,
        url: manualForm.url.trim() || undefined,
      });
      setSuccess("Job added successfully!");
      setManualForm(emptyManualForm);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job");
    } finally {
      setLoading(false);
    }
  };

  const updateManualField = (field: keyof ManualFormData, value: string) => {
    setManualForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleParse = async () => {
    if (!manualForm.description.trim()) {
      setError("Please paste a job description first");
      return;
    }

    setError(null);
    setParsing(true);
    try {
      const parsed = await parseJobDescription(manualForm.description);
      setManualForm((prev) => ({
        ...prev,
        title: parsed.title || prev.title,
        company: parsed.company || prev.company,
        location: parsed.location || prev.location,
        salary: parsed.salary || prev.salary,
      }));
      setSuccess("Fields extracted! Review and correct if needed.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse description");
    } finally {
      setParsing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex gap-2 mb-2">
          <Button
            variant={mode === "url" ? "default" : "outline"}
            size="sm"
            onClick={() => setMode("url")}
            type="button"
          >
            From URL
          </Button>
          <Button
            variant={mode === "manual" ? "default" : "outline"}
            size="sm"
            onClick={() => setMode("manual")}
            type="button"
          >
            Manual Entry
          </Button>
        </div>
        <CardTitle>{mode === "url" ? "Add Job URLs" : "Add Job Manually"}</CardTitle>
        <CardDescription>
          {mode === "url"
            ? "Enter one or more job posting URLs (one per line)"
            : "Enter job details manually (for sites that block scraping)"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {mode === "url" ? (
          <form onSubmit={handleUrlSubmit} className="space-y-4">
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
        ) : (
          <form onSubmit={handleManualSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Job Description</label>
              <Textarea
                placeholder="Paste the job description here, then click 'Extract Fields' to auto-fill the form..."
                value={manualForm.description}
                onChange={(e) => updateManualField("description", e.target.value)}
                rows={6}
                disabled={loading || parsing}
              />
              <div className="flex items-center justify-between mt-1">
                <p className="text-xs text-gray-500">
                  PII (emails, phone numbers) will be automatically removed
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleParse}
                  disabled={loading || parsing || !manualForm.description.trim()}
                >
                  {parsing ? "Extracting..." : "Extract Fields"}
                </Button>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Job Title <span className="text-red-500">*</span>
                </label>
                <Input
                  placeholder="Software Engineer"
                  value={manualForm.title}
                  onChange={(e) => updateManualField("title", e.target.value)}
                  disabled={loading || parsing}
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Company <span className="text-red-500">*</span>
                </label>
                <Input
                  placeholder="Acme Corp"
                  value={manualForm.company}
                  onChange={(e) => updateManualField("company", e.target.value)}
                  disabled={loading || parsing}
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Location</label>
                <Input
                  placeholder="San Francisco, CA"
                  value={manualForm.location}
                  onChange={(e) => updateManualField("location", e.target.value)}
                  disabled={loading || parsing}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Salary</label>
                <Input
                  placeholder="$100,000 - $150,000"
                  value={manualForm.salary}
                  onChange={(e) => updateManualField("salary", e.target.value)}
                  disabled={loading || parsing}
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">
                URL <span className="text-gray-400">(optional)</span>
              </label>
              <Input
                placeholder="https://linkedin.com/jobs/view/..."
                value={manualForm.url}
                onChange={(e) => updateManualField("url", e.target.value)}
                disabled={loading || parsing}
              />
            </div>
            <Button type="submit" disabled={loading || parsing}>
              {loading ? "Adding..." : "Add Job"}
            </Button>
          </form>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">
            {success}
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
