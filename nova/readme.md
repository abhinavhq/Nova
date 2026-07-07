# Nova

Nova is an AI-powered browser agent. It understands natural language
instructions and completes tasks on the web — navigating sites, filling
forms, extracting data, and making decisions based on what it sees —
instead of just answering questions.

## Status

🚧 Early development. Building step by step:

- [x] Step 1 — Browser control primitives (Playwright wrapper: navigate, click, type, screenshot)
- [ ] Step 2 — Perception (turn a page into a compact, LLM-readable list of interactive elements)
- [ ] Step 3 — Agent loop (LLM decides next action from perception + goal)
- [ ] Step 4 — Task decomposition + memory (break complex goals into subtasks, remember preferences)

## Requirements

```bash
pip install playwright
playwright install
```

## Usage (Step 1)

```bash
python test_browser.py
```

Opens a real browser window, navigates a couple of pages, and saves screenshots
to confirm the automation layer works end to end.