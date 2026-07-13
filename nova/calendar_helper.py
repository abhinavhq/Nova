"""
nova/calendar_helper.py

Phase 6: Calendar integration.

Extracts event details from a page (using extraction.py's existing
structured-extraction mechanism) and writes a standard .ics calendar
file - importable into Google Calendar, Outlook, Apple Calendar, or any
other calendar app. This avoids requiring a specific calendar service's
OAuth/API connector, while still genuinely producing "create a calendar
entry" as a real, usable file.
"""

from datetime import datetime
from nova.extraction import extract_structured_data


def extract_event_details(page) -> dict:
    """
    Extract event details (title, date, time, location, description)
    from the current page using the LLM-based structured extractor.
    Returns a single dict (not a list) since a page usually describes
    one event - if extraction finds multiple, the first is used.
    """
    items = extract_structured_data(
        page=page,
        fields=["title", "date", "time", "location", "description"],
        item_description="event details described on this page",
    )
    if not items:
        print("[calendar_helper] No event details found on this page.")
        return {}
    return items[0]


def _format_ics_datetime(date_str: str, time_str: str = "") -> str:
    """
    Best-effort conversion of extracted date/time strings into ICS
    format (YYYYMMDDTHHMMSS). Falls back to a date-only format if time
    can't be parsed, since extracted text is inherently messy/varied.
    """
    date_formats = ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%m/%d/%Y"]
    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            break
        except (ValueError, AttributeError):
            continue

    if not parsed_date:
        return ""  # unparseable - caller should handle this gracefully

    if time_str:
        time_formats = ["%H:%M", "%I:%M %p", "%I%p"]
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_str.strip(), fmt)
                parsed_date = parsed_date.replace(hour=parsed_time.hour, minute=parsed_time.minute)
                break
            except (ValueError, AttributeError):
                continue

    return parsed_date.strftime("%Y%m%dT%H%M%S")


def save_event_as_ics(event: dict, filepath: str = "nova_event.ics") -> str | None:
    """
    Write an extracted event dict to a standard .ics calendar file.
    Returns the filepath on success, None if the event couldn't be
    converted (e.g. unparseable date).
    """
    title = event.get("title") or "Untitled Event"
    date_str = event.get("date", "")
    time_str = event.get("time", "")
    location = event.get("location", "") or ""
    description = event.get("description", "") or ""

    dtstart = _format_ics_datetime(date_str, time_str)
    if not dtstart:
        print(f"[calendar_helper] Could not parse date '{date_str}' - skipping .ics creation.")
        return None

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Nova//Calendar Export//EN
BEGIN:VEVENT
UID:{datetime.now().strftime('%Y%m%dT%H%M%S')}-nova@local
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{dtstart}
SUMMARY:{title}
LOCATION:{location}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR
"""
    with open(filepath, "w") as f:
        f.write(ics_content)

    print(f"[calendar_helper] Saved event '{title}' to {filepath}")
    return filepath