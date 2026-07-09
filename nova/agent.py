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
import time
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
- PAGE: the current page's title, url, a short text snippet of what's
  visible on the page, and a numbered list of interactive elements

You must reply with EXACTLY ONE JSON object and nothing else. No explanation,
no markdown fences, no extra text. Valid actions:

{"action": "click", "id": <element id>}
{"action": "type", "id": <element id>, "text": "<text to type>", "press_enter": <true|false>}
{"action": "goto", "url": "<full url>"}
{"action": "scroll"}
{"action": "done", "result": "<short summary of what was accomplished>"}

Rules:
- Before deciding, check the PAGE's text snippet and heading against the
  GOAL and HISTORY. If the visible content already shows the goal has been
  achieved (e.g. you searched for a topic and the page's heading/text now
  matches that topic), respond with "done" — do NOT repeat the search or
  click search again just because a search box is visible. A search box
  being present does not mean the task is unfinished.
- Only reference element ids that appear in the current PAGE listing.
- If you're unsure what to do next, prefer "scroll" to reveal more of the page
  rather than guessing at an id that doesn't exist.
- Keep "done" results short and factual — this is shown directly to the user.
"""


class NovaAgent:
    def __init__(self, browser: NovaBrowser, max_steps: int = 15, max_runtime_seconds: int = 120):
        """
        max_steps: hard ceiling on loop iterations (existing safety net).
        max_runtime_seconds: hard ceiling on wall-clock time for the whole
            run. This matters because a step can be slow (LLM latency, page
            load, retries) even if the step COUNT looks reasonable - this
            catches the case where max_steps alone wouldn't kick in for a
            while yet, but the run is clearly taking too long.
        """
        self.browser = browser
        self.max_steps = max_steps
        self.max_runtime_seconds = max_runtime_seconds
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
        self.history: list[str] = []
        self.llm_call_count = 0

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
        self.llm_call_count += 1
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
        """
        Execute one decision, return a short text log entry for history.
        Wrapped in retries + exception handling so a single flaky action
        (element not ready, page still loading, element vanished) doesn't
        crash the whole agent run — it just gets logged and the loop
        continues, letting the LLM see the failure and adapt.
        """
        action = decision.get("action")
        max_retries = 2
        retry_delay_ms = 800

        def with_retries(fn, description: str) -> str:
            last_error = None
            for attempt in range(1, max_retries + 1):
                try:
                    return fn()
                except Exception as e:
                    last_error = e
                    print(f"[NovaAgent] Attempt {attempt}/{max_retries} failed "
                          f"for {description}: {e}")
                    if attempt < max_retries:
                        self.browser.page.wait_for_timeout(retry_delay_ms)
            return f"{description} failed after {max_retries} attempts: {last_error}"

        if action == "click":
            el = next((e for e in elements if e.id == decision.get("id")), None)
            if not el:
                return f"click failed: no element with id {decision.get('id')}"

            def do_click():
                el.locator.click(timeout=5000)
                return f"clicked [{el.id}] {el.text or el.attrs}"
            return with_retries(do_click, f"click [{el.id}]")

        if action == "type":
            el = next((e for e in elements if e.id == decision.get("id")), None)
            if not el:
                return f"type failed: no element with id {decision.get('id')}"

            def do_type():
                el.locator.fill(decision.get("text", ""), timeout=5000)
                if decision.get("press_enter"):
                    self.browser.page.keyboard.press("Enter")
                return f"typed into [{el.id}] {el.text or el.attrs}: {decision.get('text', '')!r}"
            return with_retries(do_type, f"type into [{el.id}]")

        if action == "goto":
            def do_goto():
                self.browser.goto(decision.get("url", ""))
                return f"navigated to {decision.get('url', '')}"
            return with_retries(do_goto, f"goto {decision.get('url', '')}")

        if action == "scroll":
            try:
                self.browser.scroll_down()
                return "scrolled down"
            except Exception as e:
                return f"scroll failed: {e}"

        if action == "done":
            return f"done: {decision.get('result', '')}"

        return f"unknown action: {action}"

    def run(self, goal: str) -> str:
        """Run the agent loop until 'done', max_steps, or max_runtime_seconds."""
        print(f"\n[NovaAgent] Goal: {goal}\n")
        start_time = time.time()

        for step in range(1, self.max_steps + 1):
            elapsed = time.time() - start_time
            if elapsed > self.max_runtime_seconds:
                msg = (f"Stopped: exceeded max_runtime_seconds "
                       f"({self.max_runtime_seconds}s) after {step - 1} steps "
                       f"and {self.llm_call_count} LLM calls.")
                print(f"[NovaAgent] {msg}")
                return msg

            try:
                summary, elements = get_page_summary(self.browser.page)
            except Exception as e:
                log_entry = f"perception failed: {e}"
                print(f"[Step {step}] {log_entry}")
                self.history.append(f"Step {step}: {log_entry}")
                self.browser.page.wait_for_timeout(1000)
                continue

            try:
                decision = self._ask_llm(goal, summary)
            except Exception as e:
                log_entry = f"LLM call failed: {e}"
                print(f"[Step {step}] {log_entry}")
                self.history.append(f"Step {step}: {log_entry}")
                self.browser.page.wait_for_timeout(1000)
                continue

            print(f"[Step {step}] Decision: {decision}")

            log_entry = self._execute(decision, elements)
            self.history.append(f"Step {step}: {log_entry}")
            print(f"[Step {step}] Result: {log_entry}\n")

            if decision.get("action") == "done":
                self._print_run_stats(step, start_time)
                return decision.get("result", "Task completed.")

            self.browser.page.wait_for_timeout(1000)

        self._print_run_stats(self.max_steps, start_time)
        return "Stopped: reached max_steps without the agent declaring done."

    def _print_run_stats(self, steps_taken: int, start_time: float):
        elapsed = time.time() - start_time
        print(f"[NovaAgent] Run stats: {steps_taken} steps, "
              f"{self.llm_call_count} LLM calls, {elapsed:.1f}s elapsed.")


