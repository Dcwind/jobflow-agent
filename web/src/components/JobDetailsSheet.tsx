"use client";

import { Sheet } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { parseDescription } from "@/lib/parseDescription";
import { Job } from "@/lib/api";

interface JobDetailsSheetProps {
  job: Job | null;
  onClose: () => void;
}

export function JobDetailsSheet({ job, onClose }: JobDetailsSheetProps) {
  const blocks = job?.description ? parseDescription(job.description) : [];

  return (
    <Sheet open={!!job} onClose={onClose}>
      {job && (
        <div className="flex h-full flex-col">
          {/* Top bar — sticky, quiet controls */}
          <div className="flex items-center justify-between border-b border-neutral-200/70 px-8 py-4">
            <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-neutral-500">
              <span>Job Description</span>
              {job.extraction_method && (
                <>
                  <span className="text-neutral-300">·</span>
                  <span>via {job.extraction_method}</span>
                </>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors"
              aria-label="Close"
            >
              Close ✕
            </button>
          </div>

          {/* Scrollable body */}
          <div className="flex-1 overflow-y-auto">
            <article className="mx-auto max-w-[62ch] px-8 py-10">
              {/* Masthead */}
              <header className="mb-10">
                <div className="mb-3 text-[13px] font-medium tracking-wide text-neutral-500">
                  {job.company}
                  {job.location && (
                    <>
                      <span className="mx-2 text-neutral-300">·</span>
                      {job.location}
                    </>
                  )}
                </div>
                <h1
                  className="font-serif text-[2.4rem] leading-[1.08] tracking-tight text-neutral-900"
                  style={{ fontFeatureSettings: '"ss01", "ss02"' }}
                >
                  {job.title}
                </h1>

                <div className="mt-6 flex flex-wrap items-center gap-2">
                  {job.salary && (
                    <span className="inline-flex items-center rounded-full border border-neutral-300/80 bg-white px-3 py-1 text-xs font-medium text-neutral-700">
                      {job.salary}
                    </span>
                  )}
                  <Badge variant="outline" className="rounded-full text-xs font-medium">
                    {job.stage}
                  </Badge>
                  {job.flagged && (
                    <Badge
                      variant="outline"
                      className="rounded-full border-amber-300 bg-amber-50 text-xs font-medium text-amber-800"
                    >
                      Flagged
                    </Badge>
                  )}
                </div>

                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-6 inline-flex items-center gap-1.5 text-sm text-neutral-600 underline decoration-neutral-300 decoration-1 underline-offset-4 transition-colors hover:text-neutral-900 hover:decoration-neutral-900"
                  >
                    Open original posting
                    <span aria-hidden>→</span>
                  </a>
                )}
              </header>

              {/* Divider */}
              <div className="mb-10 h-px bg-neutral-200" />

              {/* Body */}
              {blocks.length === 0 ? (
                <p className="italic text-neutral-500">
                  No description captured for this posting.
                </p>
              ) : (
                <div className="space-y-5 text-[15px] leading-[1.75] text-neutral-800">
                  {blocks.map((block, i) => {
                    if (block.kind === "heading") {
                      return (
                        <h2
                          key={i}
                          className="font-serif text-[1.4rem] leading-tight text-neutral-900 pt-4 first:pt-0"
                        >
                          {block.text}
                        </h2>
                      );
                    }
                    if (block.kind === "list") {
                      return (
                        <ul key={i} className="space-y-2.5 pl-1">
                          {block.items.map((item, j) => (
                            <li key={j} className="flex gap-3">
                              <span
                                aria-hidden
                                className="mt-[0.7em] h-1 w-1 flex-shrink-0 rounded-full bg-neutral-400"
                              />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      );
                    }
                    return (
                      <p key={i} className="text-neutral-800">
                        {block.text}
                      </p>
                    );
                  })}
                </div>
              )}
            </article>
          </div>
        </div>
      )}
    </Sheet>
  );
}
