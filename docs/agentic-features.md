# Agentic Features - Deliberation

## Vision

Add autonomous agent capabilities to Jobflow - a hybrid approach combining:
- **Background monitoring**: Proactive job discovery and notifications
- **Chat interface**: On-demand conversational interactions

## Potential Features

### 1. Proactive Job Monitoring
- Agent periodically checks job boards for new postings
- Matches against user preferences/criteria
- Notifies user of relevant matches (email, in-app, webhook)

### 2. Job Curation Based on CV
- User uploads CV or sets profile preferences
- Agent scores and ranks jobs by relevance
- Explains why a job is a good/bad match

### 3. Events Curation
- Agent finds relevant tech events, meetups, conferences
- Filters by user's interests and location
- Proactive notifications for upcoming events

## Architecture Options

### Background Workers
- Scheduled jobs (cron/task queue)
- ARQ, Celery, or simple cron
- Store results, notify asynchronously

### Conversational Agent
- Chat UI in frontend
- Agent backend (Google ADK, LangChain, or raw LLM + tools)
- Tools: search jobs, filter, explain matches, update preferences

### Shared Components
- User profile/CV storage
- Job matching/scoring logic
- Preference management

## Possible First Slices

| Slice | Description | Complexity | Dependencies |
|-------|-------------|------------|--------------|
| Job matching agent | Score existing saved jobs against user preferences | Low | Preferences storage |
| Search agent | Chat: "Find me X jobs" | Medium | Chat UI, agent backend |
| Background monitor | Scheduled job checking with notifications | Medium | Scheduler, job source APIs |

## Open Questions

- Which job sources to integrate? (LinkedIn blocks scraping, Indeed API?)
- How to handle CV parsing? (PDF extraction, structured data)
- Notification preferences - email, in-app, both?
- Rate limits and costs for LLM-powered matching at scale?

## Decision

*To be decided*

---

*Created: 2026-02-10*
