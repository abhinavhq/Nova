"""
nova/tracker.py

Phase 6: Job hunting - application tracking.
"""

import json
import os
from datetime import datetime, timedelta

DEFAULT_TRACKER_PATH = "nova_applications.json"


def _load(filepath: str = DEFAULT_TRACKER_PATH) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def _save(applications: list[dict], filepath: str = DEFAULT_TRACKER_PATH):
    with open(filepath, "w") as f:
        json.dump(applications, f, indent=2)


def add_application(
    title: str,
    company: str = "",
    url: str = "",
    deadline: str = "",
    status: str = "pending",
    filepath: str = DEFAULT_TRACKER_PATH,
) -> dict:
    applications = _load(filepath)
    entry = {
        "title": title,
        "company": company,
        "url": url,
        "deadline": deadline,
        "status": status,
        "date_added": datetime.now().strftime("%Y-%m-%d"),
    }
    applications.append(entry)
    _save(applications, filepath)
    print(f"[tracker] Added application: {title} @ {company}")
    return entry


def update_status(title: str, new_status: str, filepath: str = DEFAULT_TRACKER_PATH) -> bool:
    applications = _load(filepath)
    for app in applications:
        if app["title"] == title:
            app["status"] = new_status
            _save(applications, filepath)
            print(f"[tracker] Updated '{title}' status to '{new_status}'")
            return True
    print(f"[tracker] No application found with title '{title}'")
    return False


def list_applications(status_filter: str = "", filepath: str = DEFAULT_TRACKER_PATH) -> list[dict]:
    applications = _load(filepath)
    if status_filter:
        applications = [a for a in applications if a.get("status") == status_filter]
    return applications


def flag_upcoming_deadlines(days_threshold: int = 7, filepath: str = DEFAULT_TRACKER_PATH) -> list[dict]:
    applications = _load(filepath)
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_threshold)

    upcoming = []
    for app in applications:
        deadline_str = app.get("deadline", "")
        if not deadline_str:
            continue
        try:
            deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if today <= deadline_date <= cutoff:
            upcoming.append(app)

    return upcoming
