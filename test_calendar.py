"""
test_calendar.py

Sanity check for calendar integration: extract event details from a
page and save them as a real .ics calendar file you can import into
Google Calendar, Outlook, or Apple Calendar.

Uses a self-contained test page (deterministic, no external site
dependency) describing a sample event.
"""

from nova import NovaBrowser
from nova.calendar_helper import extract_event_details, save_event_as_ics


def main():
    TEST_EVENT_HTML = """
    <html><body>
      <h1>AI Careers Info Session</h1>
      <p>Join us for an info session on AI internship opportunities.</p>
      <p><strong>Date:</strong> 2026-08-15</p>
      <p><strong>Time:</strong> 14:00</p>
      <p><strong>Location:</strong> Online via Zoom</p>
      <p>We'll cover application tips, what companies look for, and Q&A.</p>
    </body></html>
    """

    with NovaBrowser(headless=False) as nb:
        nb.page.set_content(TEST_EVENT_HTML)

        event = extract_event_details(nb.page)
        print("\n=== EXTRACTED EVENT ===")
        print(event)

        filepath = save_event_as_ics(event, "nova_test_event.ics")
        print(f"\n.ics file created at: {filepath}")


if __name__ == "__main__":
    main()