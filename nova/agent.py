"""
nova/agent.py

The brain. This is where Cerebras enters the picture for the first time.

The loop, every step:
  1. Look at the current page (perception.py) -> compact element list
  2. Send {goal, history, element list} to the LLM
  3. LLM replies with ONE structured action as JSON
  4. We execute that action via NovaBrowser
  5. Repeat until the LLM says "done" or we hit max_steps

Action schema the LLM must reply with (and ONLY this, no prose):
  {"action": "click", "id": 3}
  {"action": "type", "id": 5, "text": "hello", "press_enter": true}
  {"action": "goto", "url": "https://..."}
  {"action": "scroll"}
  {"action": "done", "result": "short summary of what was accomplished"}
"""

import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.browser import NovaBrowser
from nova.perception import get_page_summary

load_dotenv()

MODEL = "gpt-oss-120b"  # confirmed available via /v1/models for this account

SYSTEM_PROMPT = """You are Nova, an AI browser agent. You control a web browser to
accomplish the user's goal, one action at a time.

You will be shown:
- GOAL: what the user wants accomplished
- HISTORY: actions already taken and their results
- PAGE: the current page's title, url, and a numbered list of interactive elements

You must reply with EXACTLY ONE JSON object and nothing else. No explanation,
no markdown fences, no extra text. Valid actions:

{"action": "click", "id": <element id>}
{"action": "type", "id": <element id>, "text": "<text to type>", "press_enter": <true|false>}
{"action": "goto", "url": "<full url>"}
{"action": "scroll"}
{"action": "done", "result": "<short summary of what was accomplished>"}

Rules:
- Only reference element ids that appear in the current PAGE listing.
- If the goal is already accomplished, respond with the "done" action.
- If you're unsure what to do next, prefer "scroll" to reveal more of the page
  rather than guessing at an id that doesn't exist.
- Keep "done" results short and factual — this is shown directly to the user.
"""


class NovaAgent:
    def __init__(self, browser: NovaBrowser, max_steps: int = 15):
        self.browser = browser
        self.max_steps = max_steps
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
        self.history: list[str] = []

    def _build_user_message(self, goal: str, summary: str) -> str:
        history_text = "\n".join(self.history) if self.history else "(no actions yet)"
        return f"""GOAL: {goal}

HISTORY:
{history_text}

PAGE:
title: {self.browser.get_title()}
url: {self.browser.get_url()}
elements:
{summary}
"""

    def _ask_llm(self, goal: str, summary: str) -> dict:
        user_msg = self._build_user_message(goal, summary)
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        raw = response.choices[0].message.content.strip()
        # be defensive: strip accidental markdown fences if the model adds them
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print(f"[NovaAgent] Failed to parse LLM response as JSON:\n{raw}")
            return {"action": "done", "result": "Stopped: could not parse a valid next action."}

    def _execute(self, decision: dict, elements) -> str:
        """Execute one decision, return a short text log entry for history."""
        action = decision.get("action")

        if action == "click":
            el = next((e for e in elements if e.id == decision.get("id")), None)
            if not el:
                return f"click failed: no element with id {decision.get('id')}"
            el.locator.click()
            return f"clicked [{el.id}] {el.text or el.attrs}"

        if action == "type":
            el = next((e for e in elements if e.id == decision.get("id")), None)
            if not el:
                return f"type failed: no element with id {decision.get('id')}"
            el.locator.fill(decision.get("text", ""))
            if decision.get("press_enter"):
                self.browser.page.keyboard.press("Enter")
            return f"typed into [{el.id}] {el.text or el.attrs}: {decision.get('text', '')!r}"

        if action == "goto":
            self.browser.goto(decision.get("url", ""))
            return f"navigated to {decision.get('url', '')}"

        if action == "scroll":
            self.browser.scroll_down()
            return "scrolled down"

        if action == "done":
            return f"done: {decision.get('result', '')}"

        return f"unknown action: {action}"

    def run(self, goal: str) -> str:
        """Run the agent loop until 'done' or max_steps is reached."""
        print(f"\n[NovaAgent] Goal: {goal}\n")

        for step in range(1, self.max_steps + 1):
            summary, elements = get_page_summary(self.browser.page)
            decision = self._ask_llm(goal, summary)
            print(f"[Step {step}] Decision: {decision}")

            log_entry = self._execute(decision, elements)
            self.history.append(f"Step {step}: {log_entry}")
            print(f"[Step {step}] Result: {log_entry}\n")

            if decision.get("action") == "done":
                return decision.get("result", "Task completed.")

            self.browser.page.wait_for_timeout(1000)

        return "Stopped: reached max_steps without the agent declaring done.""""
nova/agent.py

The brain. This is where Cerebras enters the picture for the first time.

The loop, every step:
  1. Look at the current page (perception.py) -> compact element list
  2. Send {goal, history, element list} to the LLM
  3. LLM replies with ONE structured action as JSON
  4. We execute that action via NovaBrowser
  5. Repeat until the LLM says "done" or we hit max_steps

Action schema the LLM must reply with (and ONLY this, no prose):
  {"action": "click", "id": 3}
  {"action": "type", "id": 5, "text": "hello", "press_enter": true}
  {"action": "goto", "url": "https://..."}
  {"action": "scroll"}
  {"action": "done", "result": "short summary of what was accomplished"}
"""

import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.browser import NovaBrowser
from nova.perception import get_page_summary

load_dotenv()

MODEL = "gpt-oss-120b"  # confirmed available via /v1/models for this account

SYSTEM_PROMPT = """You are Nova, an AI browser agent. You control a web browser to
accomplish the user's goal, one action at a time.

You will be shown:
- GOAL: what the user wants accomplished
- HISTORY: actions already taken and their results
- PAGE: the current page's title, url, and a numbered list of interactive elements

You must reply with EXACTLY ONE JSON object and nothing else. No explanation,
no markdown fences, no extra text. Valid actions:

{"action": "click", "id": <element id>}
{"action": "type", "id": <element id>, "text": "<text to type>", "press_enter": <true|false>}
{"action": "goto", "url": "<full url>"}
{"action": "scroll"}
{"action": "done", "result": "<short summary of what was accomplished>"}

Rules:
- Only reference element ids that appear in the current PAGE listing.
- If the goal is already accomplished, respond with the "done" action.
- If you're unsure what to do next, prefer "scroll" to reveal more of the page
  rather than guessing at an id that doesn't exist.
- Keep "done" results short and factual — this is shown directly to the user.
"""


class NovaAgent:
    def __init__(self, browser: NovaBrowser, max_steps: int = 15):
        self.browser = browser
        self.max_steps = max_steps
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
        self.history: list[str] = []

    def _build_user_message(self, goal: str, summary: str) -> str:
        history_text = "\n".join(self.history) if self.history else "(no actions yet)"
        return f"""GOAL: {goal}

HISTORY:
{history_text}

PAGE:
title: {self.browser.get_title()}
url: {self.browser.get_url()}
elements:
{summary}
"""

    def _ask_llm(self, goal: str, summary: str) -> dict:
        user_msg = self._build_user_message(goal, summary)
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        raw = response.choices[0].message.content.strip()
        # be defensive: strip accidental markdown fences if the model adds them
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print(f"[NovaAgent] Failed to parse LLM response as JSON:\n{raw}")
            return {"action": "done", "result": "Stopped: could not parse a valid next action."}

    def _execute(self, decision: dict, elements) -> str:
        """Execute one decision, return a short text log entry for history."""
        action = decision.get("action")

        if action == "click":
            el = next((e for e in elements if e.id == decision.get("id")), None)
            if not el:
                return f"click failed: no element with id {decision.get('id')}"
            el.locator.click()
            return f"clicked [{el.id}] {el.text or el.attrs}"

        if action == "type":
            el = next((e for e in elements if e.id == decision.get("id")), None)
            if not el:
                return f"type failed: no element with id {decision.get('id')}"
            el.locator.fill(decision.get("text", ""))
            if decision.get("press_enter"):
                self.browser.page.keyboard.press("Enter")
            return f"typed into [{el.id}] {el.text or el.attrs}: {decision.get('text', '')!r}"

        if action == "goto":
            self.browser.goto(decision.get("url", ""))
            return f"navigated to {decision.get('url', '')}"

        if action == "scroll":
            self.browser.scroll_down()
            return "scrolled down"

        if action == "done":
            return f"done: {decision.get('result', '')}"

        return f"unknown action: {action}"

    def run(self, goal: str) -> str:
        """Run the agent loop until 'done' or max_steps is reached."""
        print(f"\n[NovaAgent] Goal: {goal}\n")

        for step in range(1, self.max_steps + 1):
            summary, elements = get_page_summary(self.browser.page)
            decision = self._ask_llm(goal, summary)
            print(f"[Step {step}] Decision: {decision}")

            log_entry = self._execute(decision, elements)
            self.history.append(f"Step {step}: {log_entry}")
            print(f"[Step {step}] Result: {log_entry}\n")

            if decision.get("action") == "done":
                return decision.get("result", "Task completed.")

            self.browser.page.wait_for_timeout(1000)

        return "Stopped: reached max_steps without the agent declaring done."