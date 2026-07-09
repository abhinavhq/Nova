"""
nova/planner.py

Phase 2: Multi-step planning.

A single NovaAgent.run(goal) handles one flat browsing goal well, but a
real request like "find AI internships in Japan, compare them, and save
the top 5" is actually several distinct subtasks chained together.

NovaPlanner's job: take a complex goal and ask the LLM to break it into
an ordered list of smaller, concrete subtasks - each one small enough
that a single NovaAgent.run() call can execute it.

NovaOrchestrator's job: run the plan - execute each subtask via
NovaAgent, carry forward what was learned/accomplished as context for
the next subtask, and produce a final combined result.
"""

import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.browser import NovaBrowser
from nova.agent import NovaAgent, MODEL

load_dotenv()

PLANNER_SYSTEM_PROMPT = """You are a task planner for Nova, an AI browser agent.

Given a user's goal, break it down into an ordered list of small, concrete
subtasks. Each subtask should be achievable by a single browsing session
that navigates, searches, clicks, and extracts information - nothing that
requires actions outside a web browser.

Rules:
- 2 to 6 subtasks. Prefer fewer, clearer subtasks over many tiny ones.
- Each subtask should be self-contained enough to understand without
  needing the original goal restated, but can reference "the results from
  the previous step" in plain English if it depends on prior output.
- If the goal is already simple enough to be one subtask, return a list
  with just one item.
- Reply with EXACTLY ONE JSON object and nothing else - no explanation,
  no markdown fences. Format:
  {"subtasks": ["first subtask", "second subtask", ...]}
"""


class NovaPlanner:
    def __init__(self):
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

    def plan(self, goal: str) -> list[str]:
        """Ask the LLM to break `goal` into an ordered list of subtasks."""
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": f"GOAL: {goal}"},
            ],
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            parsed = json.loads(raw)
            subtasks = parsed.get("subtasks", [])
            if not subtasks:
                raise ValueError("empty subtasks list")
            return subtasks
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[NovaPlanner] Failed to parse plan, falling back to "
                  f"single-step: {e}\nRaw response: {raw}")
            return [goal]  # fallback: treat the whole goal as one subtask


class NovaOrchestrator:
    """
    Runs a full multi-step plan: plans the subtasks, executes each one
    via a NovaAgent (reusing the same browser session so state like
    login/navigation carries over naturally), and collects results.
    """

    def __init__(self, browser: NovaBrowser, max_steps_per_subtask: int = 10):
        self.browser = browser
        self.max_steps_per_subtask = max_steps_per_subtask
        self.planner = NovaPlanner()

    def run(self, goal: str) -> dict:
        subtasks = self.planner.plan(goal)
        print(f"\n[NovaOrchestrator] Plan for goal: {goal}")
        for i, st in enumerate(subtasks, 1):
            print(f"  {i}. {st}")

        results = []
        for i, subtask in enumerate(subtasks, 1):
            # carry forward prior results as plain-text context so later
            # subtasks can reference earlier findings
            context = ""
            if results:
                context = "\n\nCONTEXT FROM PREVIOUS STEPS:\n" + "\n".join(
                    f"- Step {j+1} ({subtasks[j]}): {r}"
                    for j, r in enumerate(results)
                )

            full_goal = f"{subtask}{context}"
            print(f"\n[NovaOrchestrator] Running subtask {i}/{len(subtasks)}: {subtask}")

            agent = NovaAgent(browser=self.browser, max_steps=self.max_steps_per_subtask)
            result = agent.run(full_goal)
            results.append(result)
            print(f"[NovaOrchestrator] Subtask {i} result: {result}")

        return {
            "goal": goal,
            "subtasks": subtasks,
            "results": results,
            "final_summary": results[-1] if results else "No subtasks executed.",
        }