# Progress

Commit after every class. Tag every Friday: `git tag week-N && git push origin week-N`.

## Week 1 (tag week-1 by Fri 23 Oct)
- [x] Repo created from the Examate template and registered on the form
- [x] README top section filled from my project card
- [x] /health runs locally
- [x] docs/QUESTIONS.md: 10 real questions
- [x] 50+ pages collected, DATASET.md filled, sample in data/sample/
- [x] Tag week-1 pushed

## Week 2 (tag week-2 by Fri 30 Oct)
- [x] POST /chat calls an LLM and returns structured JSON
- [x] Streaming, timeouts, retry and a fallback model
- [x] Cost log + GET /usage
- [x] Docker Compose (API + Postgres/pgvector) runs
- [x] CI green, live link in README
- [x] Tag week-2 pushed

## Week 3 (tag week-3 by Fri 6 Nov)
- [ ] Parser keeps page numbers and headings
- [ ] 500+ pages chunked, embedded and stored in pgvector
- [ ] POST /ask answers with [document, page] citations
- [ ] docs/EVAL_v0.md with my 10 questions scored
- [ ] Tag week-3 pushed

## Daily log
| Date | What I did today | Commit |
|---|---|---|
| 2026-10-21 | Initialized repository from Examate template, basic environment setup and /health | 8e3030b |
| 2026-10-22 | Documented problem space, user persona, and dataset plan in README | 73ace89 |
| 2026-10-23 | Completed 10 evaluation questions (QUESTIONS.md), downloaded first CERC documents, filled DATASET.md, tagged week-1 | `feat: complete week-1 dataset collection and evaluation questions` |
| 2026-10-26 | Implemented core LLM client schemas, token estimation, and provider abstractions | `feat: implement LLM schemas, token estimator, and provider protocol` |
| 2026-10-27 | Implemented streaming SSE /chat, backoff with jitter, fallback model, cost logging & GET /usage | `feat: add SSE streaming, retry with jitter, fallback provider, and /usage` |
| 2026-10-29 | Created Docker Compose configuration with PostgreSQL 16 + pgvector and /ready healthcheck | `feat: add Docker Compose with pgvector and /ready endpoint` |
| 2026-10-30 | Added comprehensive test suite (15 passed), DESIGN.md, COST.md, and CI verification, tagged week-2 | `feat: complete week-2 deliverables with DESIGN.md, COST.md, and test suite` |
