"""
nova/summarize.py

Phase 3: Summarization.

For long articles/threads/reports, dumping raw extracted text isn't
useful - the person wants the key points, not the whole page. This
condenses a page's visible text into a short summary via the LLM.
"""

import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.perception import get_page_full_text
from nova.agent import MODEL

load_dotenv()

SUMMARIZE_SYSTEM_PROMPT = """You summarize webpage content for Nova, an AI
browser agent. Given raw visible text from a page, produce a concise
summary in plain English.

Rules:
- 3-6 sentences, or a short bulleted list if the content is naturally
  list-like (steps, features, findings).
- Cover the key points only - specifics that matter (numbers, names,
  conclusions), not filler.
- Do not copy long verbatim passages from the source - always rephrase
  in your own words.
- Reply with the summary only, no preamble like "Here's a summary:".
"""


def summarize_page(page, focus_hint: str = "") -> str:
    """
    Summarize the current page's visible text content.

    focus_hint: optional guidance on what to focus the summary on, e.g.
        "focus on the pricing details" or "focus on the main argument"
    """
    client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
    page_text = get_page_full_text(page)

    user_msg = f"PAGE TEXT:\n{page_text}"
    if focus_hint:
        user_msg += f"\n\nFOCUS: {focus_hint}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    return response.choices[0].message.content.strip()