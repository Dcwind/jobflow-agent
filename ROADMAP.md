# Jobflow Roadmap

## Vision
An intelligent job application tracking platform that helps job seekers organize, analyze, and optimize their job search.

## Current: Web MVP
- [x] Job URL extraction (title, company, location, salary, description)
- [x] Fallback chain: BeautifulSoup → Playwright → LLM
- [ ] SQLite storage with PII filtering
- [ ] FastAPI backend with CRUD + export
- [ ] Next.js frontend with job table
- [ ] Railway deployment

## Near-term (Post-MVP)
- **Fit Score Agent** — Compare jobs against user's CV/skills, rank opportunities
- **Pattern Analysis** — Identify trends in applications (skills gaps, common requirements)
- **User Authentication** — Multi-user support with data isolation

## Medium-term
- **Hackathon/Event Suggestions** — Surface relevant networking opportunities
- **Networking Guides** — Curated resources for professional growth
- **Browser Extension** — One-click job extraction (Chrome Manifest V3)

## Long-term
- **Mobile App** — Track applications on the go
- **ATS Integrations** — Connect to Greenhouse, Lever, Workday APIs
- **AI Application Drafting** — Generate tailored cover letters and responses

## Technical Debt & Improvements
- [ ] Add Alembic migrations for schema changes
- [ ] Implement caching for repeated URL fetches
- [ ] Add rate limiting per user (when auth is added)
- [ ] Set up LangSmith/Langfuse for agent observability
