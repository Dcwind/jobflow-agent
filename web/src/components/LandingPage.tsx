"use client";

import Link from "next/link";

const FEATURES = [
  {
    title: "Save",
    description:
      "Add a job URL and Jobflow tries to extract the posting. If the site blocks access, paste the description yourself — either way, it's saved.",
  },
  {
    title: "Read",
    description:
      "Descriptions are formatted with proper headings, bullets, and spacing so you can actually read them when you need to.",
  },
  {
    title: "Track",
    description:
      "Drag jobs through your pipeline from Backlog to Offer on a kanban board.",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#fbfaf7]">
      {/* Nav */}
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <span className="text-lg font-bold text-neutral-900">Jobflow</span>
        <Link
          href="/signin"
          className="text-sm font-medium text-neutral-600 transition-colors hover:text-neutral-900"
        >
          Sign in
        </Link>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-3xl px-6 pt-20 pb-24 text-center sm:pt-32 sm:pb-36">
        <h1
          className="font-serif text-[2.5rem] leading-[1.08] tracking-tight text-neutral-900 sm:text-[4rem]"
          style={{ fontFeatureSettings: '"ss01", "ss02"' }}
        >
          Never lose track of a job&nbsp;description&nbsp;again.
        </h1>
        <p className="mx-auto mt-6 max-w-[48ch] text-lg leading-relaxed text-neutral-600 sm:text-xl">
          Save job postings as you apply. When you get the interview weeks
          later, the description is right where you left it.
        </p>
        <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
          <Link
            href="/signin"
            className="inline-flex h-11 items-center rounded-lg bg-neutral-900 px-7 text-sm font-medium text-white transition-colors hover:bg-neutral-800"
          >
            Get started — it&apos;s free
          </Link>
          <a
            href="https://github.com/Dcwind/jobflow-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-11 items-center rounded-lg border border-neutral-300 bg-white px-7 text-sm font-medium text-neutral-700 transition-colors hover:border-neutral-400 hover:text-neutral-900"
          >
            View on GitHub
          </a>
        </div>
      </section>

      {/* Divider */}
      <div className="mx-auto max-w-5xl px-6">
        <div className="h-px bg-neutral-200" />
      </div>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-6 py-20 sm:py-28">
        <div className="grid gap-12 sm:grid-cols-3 sm:gap-8">
          {FEATURES.map((f) => (
            <div key={f.title}>
              <h3 className="font-serif text-xl text-neutral-900">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-neutral-600">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Divider */}
      <div className="mx-auto max-w-5xl px-6">
        <div className="h-px bg-neutral-200" />
      </div>

      {/* Footer */}
      <footer className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-col items-center justify-between gap-4 text-sm text-neutral-500 sm:flex-row">
          <span>Built by Daniel Ekwuazi</span>
          <div className="flex gap-6">
            <a
              href="https://github.com/Dcwind/jobflow-agent"
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-neutral-900"
            >
              GitHub
            </a>
            <Link
              href="/privacy"
              className="transition-colors hover:text-neutral-900"
            >
              Privacy
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
