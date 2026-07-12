"""
nova/generate.py

Phase 4: Generated content.

Extraction and comparison get you structured data. This turns that data
into content a person would actually send/use: a cover letter tailored
to a specific job posting, an email summarizing a page, or a day-by-day
itinerary from a set of compared options.
"""

import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from nova.agent import MODEL

load_dotenv()


def _ask(system_prompt: str, user_msg: str) -> str:
    client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_cover_letter(job_description: str, base_resume: str, candidate_name: str = "") -> str:
    """
    Draft a cover letter tailored to a specific job description, using
    the candidate's base resume/background as source material.
    """
    system_prompt = """You write concise, genuine-sounding cover letters.
Rules:
- 3-4 short paragraphs, under 300 words total.
- Reference 2-3 SPECIFIC things from the job description (skills, tech,
  responsibilities) and connect them to relevant background from the
  resume - don't just restate the resume generically.
- No generic filler like "I am writing to express my interest" - open
  with something specific to this role.
- Professional but human tone, not overly formal or robotic.
- Do not invent experience not present in the provided resume/background.
"""
    user_msg = f"""JOB DESCRIPTION:
{job_description}

CANDIDATE BACKGROUND:
{base_resume}
"""
    if candidate_name:
        user_msg += f"\nCANDIDATE NAME: {candidate_name}"

    return _ask(system_prompt, user_msg)


def draft_email_from_content(page_text_or_summary: str, purpose: str, recipient_context: str = "") -> str:
    """
    Draft an email based on webpage content Nova found, for a stated
    purpose (e.g. "summarize this for my manager", "share this article
    with a friend").
    """
    system_prompt = """You draft emails for Nova, an AI browser agent, based
on webpage content it found. Include a subject line and a body.
Rules:
- Keep it concise and purpose-driven - match tone to the stated purpose.
- Reply in this exact format:
  SUBJECT: <subject line>
  BODY:
  <email body>
- Do not copy long verbatim passages from the source content - rephrase.
"""
    user_msg = f"CONTENT:\n{page_text_or_summary}\n\nPURPOSE: {purpose}"
    if recipient_context:
        user_msg += f"\nRECIPIENT CONTEXT: {recipient_context}"

    return _ask(system_prompt, user_msg)


def generate_itinerary(items: list[dict], trip_context: str) -> str:
    """
    Turn a list of compared options (e.g. extracted flights/hotels/activities)
    into a readable day-by-day (or ranked) itinerary write-up.
    """
    system_prompt = """You write clear, practical itinerary/summary
write-ups from a list of compared options for Nova, an AI browser agent.
Rules:
- Organize logically (by day, by rank, or by category - whatever fits
  the data given).
- Reference concrete details from the data (names, prices, dates) - do
  not invent details not present in the data.
- Keep it skimmable: short paragraphs or a light list structure.
"""
    items_text = "\n".join(str(item) for item in items)
    user_msg = f"OPTIONS DATA:\n{items_text}\n\nCONTEXT: {trip_context}"

    return _ask(system_prompt, user_msg)