/**
 * Parse a raw job description string into structured blocks for rendering.
 *
 * Job descriptions come from scraped HTML or LLM extraction — they're plain text
 * with inconsistent formatting. We heuristically detect headings, bullets, and
 * paragraphs so the reader UI can render them with proper typography.
 */

export type Block =
  | { kind: "heading"; text: string }
  | { kind: "paragraph"; text: string }
  | { kind: "list"; items: string[] };

const BULLET_RE = /^\s*(?:[-*•·●○◦▪▫→»]|\d+[.)])\s+/;

const KNOWN_HEADINGS = [
  "about us",
  "about the role",
  "about the job",
  "about you",
  "the role",
  "the opportunity",
  "responsibilities",
  "requirements",
  "qualifications",
  "what you'll do",
  "what you will do",
  "what you'll bring",
  "what you will bring",
  "what we're looking for",
  "what we are looking for",
  "what we offer",
  "who you are",
  "benefits",
  "perks",
  "perks & benefits",
  "compensation",
  "nice to have",
  "nice-to-have",
  "preferred qualifications",
  "minimum qualifications",
  "your impact",
  "your profile",
  "skills",
  "experience",
  "education",
  "how to apply",
];

function isHeading(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed || trimmed.length > 80) return false;

  // "Requirements:" / "What you'll do:"
  if (trimmed.endsWith(":") && trimmed.length <= 60 && !BULLET_RE.test(trimmed)) {
    return true;
  }

  const lower = trimmed.toLowerCase().replace(/[:\s]+$/, "");
  if (KNOWN_HEADINGS.includes(lower)) return true;

  // ALL CAPS short lines (e.g. "RESPONSIBILITIES")
  const letters = trimmed.replace(/[^A-Za-z]/g, "");
  if (
    letters.length >= 3 &&
    letters === letters.toUpperCase() &&
    trimmed.split(/\s+/).length <= 6
  ) {
    return true;
  }

  return false;
}

function stripBullet(line: string): string {
  return line.replace(BULLET_RE, "").trim();
}

export function parseDescription(raw: string): Block[] {
  if (!raw) return [];

  const lines = raw.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];

  let paragraph: string[] = [];
  let list: string[] = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push({ kind: "paragraph", text: paragraph.join(" ").trim() });
      paragraph = [];
    }
  };

  const flushList = () => {
    if (list.length) {
      blocks.push({ kind: "list", items: list });
      list = [];
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    if (isHeading(line)) {
      flushParagraph();
      flushList();
      blocks.push({
        kind: "heading",
        text: line.replace(/[:\s]+$/, ""),
      });
      continue;
    }

    if (BULLET_RE.test(rawLine)) {
      flushParagraph();
      const item = stripBullet(rawLine);
      if (item) list.push(item);
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  flushParagraph();
  flushList();

  return blocks;
}
