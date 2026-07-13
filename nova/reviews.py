"""
nova/reviews.py

Phase 6: Shopping - review aggregation.

Instead of reading dozens of reviews yourself, this summarizes overall
sentiment and pulls out the most commonly mentioned pros/cons.
"""

import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.agent import MODEL

load_dotenv()

REVIEWS_SYSTEM_PROMPT = """You aggregate product/service reviews for Nova,
an AI browser agent. Given raw review text (possibly multiple reviews
concatenated), produce:
1. An overall sentiment (positive / mixed / negative) with a one-line reason.
2. 2-4 commonly mentioned pros.
3. 2-4 commonly mentioned cons (if any appear).

Rules:
- Base this ONLY on patterns that actually appear multiple times or are
  clearly emphasized in the text - do not invent a consensus that isn't
  there.
- Keep each point short (under 15 words).
- Reply in this exact format:
  SENTIMENT: <positive/mixed/negative> - <one line reason>
  PROS:
  - <pro 1>
  - <pro 2>
  CONS:
  - <con 1>
  - <con 2>
"""


def aggregate_reviews(review_text: str) -> str:
    """
    Summarize sentiment and common points across review text. Pass in
    raw review text (e.g. from get_page_full_text() on a reviews page,
    or multiple reviews joined together).
    """
    client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REVIEWS_SYSTEM_PROMPT},
            {"role": "user", "content": f"REVIEWS:\n{review_text}"},
        ],
    )
    return response.choices[0].message.content.strip()