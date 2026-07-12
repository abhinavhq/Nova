"""
test_generate.py

Sanity check for Phase 4: generate a cover letter, an email draft, and
an itinerary write-up - all from realistic sample inputs, no browser
needed for this one since we're testing the generation layer directly.
"""

from nova.generate import generate_cover_letter, draft_email_from_content, generate_itinerary


def main():
    # --- Cover letter ---
    job_description = """AI Internship - Tokyo, Japan
We're looking for a student with Python experience and interest in
browser automation / LLM agents to help build internal tooling.
Familiarity with Playwright or Selenium is a plus. Remote-friendly,
3-month internship."""

    resume = """2nd-semester CS student. Built an AI browser automation
agent (Nova) using Python, Playwright, and Cerebras LLM APIs. Also built
a voice assistant (JOI) with speech recognition, TTS, and semantic memory.
Comfortable with Python, Git, and API integration."""

    print("=== COVER LETTER ===")
    letter = generate_cover_letter(job_description, resume, candidate_name="Abhinav")
    print(letter)

    # --- Email draft ---
    print("\n=== EMAIL DRAFT ===")
    summary = ("Artificial intelligence enables computers to perform tasks "
               "requiring human-like reasoning. Recent growth is driven by "
               "GPU-accelerated deep learning and transformer architectures.")
    email = draft_email_from_content(
        page_text_or_summary=summary,
        purpose="share this as an interesting read with a friend who's into tech",
    )
    print(email)

    # --- Itinerary from sample comparison data ---
    print("\n=== ITINERARY ===")
    sample_options = [
        {"title": "Sharp Objects", "price": "£47.82", "source_url": "site A"},
        {"title": "The Widow", "price": "£27.26", "source_url": "site A"},
        {"title": "Under the Tuscan Sun", "price": "£37.33", "source_url": "site B"},
    ]
    itinerary = generate_itinerary(sample_options, trip_context="Weekend reading list, budget-ranked")
    print(itinerary)


if __name__ == "__main__":
    main()