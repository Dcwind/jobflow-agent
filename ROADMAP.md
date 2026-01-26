# Jobflow Roadmap

## Vision
An intelligent job application tracking platform that helps job seekers organize, analyze, and optimize their job search.

## Current: Web MVP
- [x] Job URL extraction (title, company, location, salary, description)
- [x] Fallback chain: BeautifulSoup → Playwright → LLM
- [x] SQLite storage with PII filtering
- [x] FastAPI backend with CRUD + export
- [x] Next.js frontend with job table
- [x] Railway backend deployment
- [x] Vercel frontend deployment

## Next Up
- [x] **API Protection** — Next.js API proxy with server-side API key (block direct backend abuse)

## Near-term (Post-MVP)
- **User Authentication** — Better Auth (self-hosted, own your data)
  - Email/password + social OAuth
  - Session management
  - Multi-user data isolation
- **PostgreSQL Migration** — Replace SQLite for multi-user support
- **Fit Score Agent** — Compare jobs against user's CV/skills, rank opportunities
- **Pattern Analysis** — Identify trends in applications (skills gaps, common requirements)

## Medium-term
- **Browser Extension** — One-click job extraction (Chrome Manifest V3)
- **Hackathon/Event Suggestions** — Surface relevant networking opportunities
- **Networking Guides** — Curated resources for professional growth
- **Subscriptions** — Stripe direct integration (free tier, pro tier)

## Long-term
- **Mobile App** — Track applications on the go
- **ATS Integrations** — Connect to Greenhouse, Lever, Workday APIs
- **AI Application Drafting** — Generate tailored cover letters and responses

## Technical Debt & Improvements
- [x] Fix: Handle jobLocation as array in JSON-LD extraction
- [x] Fix: Display job description in frontend (expandable row)
- [x] Fix: Table layout shifting when flagging jobs (overflow-hidden on container)
- [ ] Fix: Right padding disappears at <351px viewport width (CSS spec limitation)
- [ ] Add Alembic migrations for schema changes
- [ ] Implement caching for repeated URL fetches
- [ ] Add rate limiting per user (when auth is added)
- [ ] Set up LangSmith/Langfuse for agent observability
- [ ] Migrate from Nixpacks to Dockerfile ([plan](docs/dockerfile-migration.md))
