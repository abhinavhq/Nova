# Nova Roadmap

Nova is an AI-powered browser agent: understands natural language goals,
controls a real browser, and completes multi-step web tasks — research,
job hunting, shopping, travel planning, coding help, everyday automation.

Built step-by-step, testing each piece before moving to the next.

---

## Phase 0 — Core Agent Loop (DONE)
- [x] Browser control primitives (Playwright: navigate, click, type, screenshot, scroll)
- [x] Perception (page -> numbered list of interactive elements + visible text context)
- [x] Agent loop (LLM decides one action at a time based on goal + history + page state)
- [x] Cerebras integration (gpt-oss-120b)

## Phase 1 — Reliability (DONE)
- [x] Fix "done" detection so it doesn't loop/repeat actions
- [x] Error recovery: retry when an element disappears or page doesn't load
- [x] Handle popups/cookie banners automatically
- [x] Rate/step/cost limiting so a bad loop can't burn API credits or run forever

## Phase 2 — Multi-Step Planning (DONE)
- [x] Planner: break a complex goal into ordered subtasks
- [x] Subtask runner: run the agent loop per subtask, carry results forward
- [x] Task queue: give Nova multiple goals, run sequentially, report back

## Phase 3 — Data Extraction & Output (DONE)
- [x] Structured extraction: pull specific fields off a page into Python objects (title, price, deadline, etc.)
- [x] Spreadsheet output (.xlsx) from extracted data
- [x] Multi-source comparison: same data point across 3-5 sites, tabulated
- [x] Summarization: condense long pages/threads instead of raw extraction
- [x] PDF handling: download + read PDFs encountered mid-task

## Phase 4 — Generated Content
- [x] Personalized cover letters from job description + base resume
- [x] Resume/cover letter tailoring to match keywords
- [x] Email drafting from web content ("summarize this page into an email")
- [x] Itinerary write-ups (travel day-by-day plans) — CAVEAT: found to sometimes misstate source facts (e.g. shifted a flight date incorrectly in test_travel.py); treat as a narrative convenience layer, not a source of truth

## Phase 5 — Safety & Confirmation (DONE)
- [x] Sensitive-action confirmation (submit, purchase, send) — pause and ask before executing
- [x] Dry-run mode: "show me what you'd do" without executing
- [x] Auto-fill from saved profile (name, email, experience) — always confirm before submit

## Phase 6 — Domain Workflows
- [x] Job hunting: application tracking spreadsheet across sessions, deadline flags
- [x] Shopping: price tracking + alerts, review sentiment aggregation, cart building
- [x] Travel: flight/hotel comparison + ranking/filtering confirmed accurate (find_best_options, filter_by_max_price); flexible date/price search works
- [x] Booking with confirmation — covered by NovaAgent's existing sensitive-action gate ("book now"/"reserve" already in SENSITIVE_KEYWORDS from Phase 5, not separately re-tested)
- [ ] Coding: docs lookup, GitHub issue triage, Stack Overflow research
- [ ] Calendar: extract event details from a page, create calendar entries (needs connector)

## Phase 7 — Platform & Integration
- [ ] Headless/background mode toggle once trust is established
- [ ] Session memory: preferences persist across runs (could reuse JOI's SQLite memory)
- [ ] Voice control via JOI ("Nova, find me AI internships")
- [ ] Multi-site workflows: search one site, cross-reference another, combine results

---

## Working principle
Every checkbox above gets its own small test script before moving to the next.
No skipping ahead — each phase depends on the reliability of the one before it.