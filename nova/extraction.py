"""
nova/extraction.py

Phase 3: Structured data extraction.

Up to now, Nova reports back plain text ("done: Data mining"). That's fine
for simple lookups, but the original goal - "find AI internships, compare
requirements, save the top 10 in a spreadsheet" - needs actual structured
rows of data, not a sentence.

extract_structured_data() takes the current page's visible text and a
description of what fields you want, and asks the LLM to return a list
of dicts matching that schema. This is used ON TOP OF the agent loop:
first navigate/search normally (NovaAgent), then call this once you're
on a page that has the data you want.
"""

import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.perception import get_page_full_text
from nova.agent import MODEL

load_dotenv()

EXTRACTION_SYSTEM_PROMPT = """You extract structured data from webpage text
for Nova, an AI browser agent.

You will be given raw visible text from a webpage and a list of fields to
extract for each item found on the page (e.g. a list of products, articles,
listings). Find every distinct item on the page that matches what's being
asked for, and extract the requested fields for each one.

Rules:
- Reply with EXACTLY ONE JSON object and nothing else - no explanation,
  no markdown fences. Format:
  {"items": [{"field1": "value", "field2": "value"}, ...]}
- If a field isn't present for a given item, use null for that field -
  do not guess or invent values.
- If NO matching items are found on the page, return {"items": []}.
- Keep values concise - short text, not full paragraphs.
"""


def extract_structured_data(page, fields: list[str], item_description: str = "items") -> list[dict]:
    """
    Extract a list of structured dicts from the current page.

    fields: e.g. ["title", "price", "rating"]
    item_description: what kind of thing you're extracting, e.g.
        "books listed on this page" or "job postings on this page"
    """
    client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
    page_text = get_page_full_text(page)

    user_msg = f"""Extract {item_description} from the following page text.

Fields to extract for each item: {", ".join(fields)}

PAGE TEXT:
{page_text}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        parsed = json.loads(raw)
        return parsed.get("items", [])
    except json.JSONDecodeError as e:
        print(f"[extraction] Failed to parse extraction response: {e}\nRaw: {raw}")
        return []