"""
test_tracker.py

Sanity check for the application tracker.
"""

from datetime import datetime, timedelta
from nova.tracker import add_application, update_status, list_applications, flag_upcoming_deadlines


def main():
    soon = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    far = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

    add_application(title="AI Intern - Tokyo Startup", company="Tokyo Startup Inc",
                     url="https://example.com/job1", deadline=soon)
    add_application(title="ML Intern - Osaka Lab", company="Osaka Lab",
                     url="https://example.com/job2", deadline=far)
    add_application(title="Backend Intern - Remote", company="Remote Co",
                     url="https://example.com/job3")

    print("\n=== ALL APPLICATIONS ===")
    for app in list_applications():
        print(f"  {app}")

    update_status("AI Intern - Tokyo Startup", "applied")

    print("\n=== PENDING ONLY ===")
    for app in list_applications(status_filter="pending"):
        print(f"  {app}")

    print("\n=== UPCOMING DEADLINES (next 7 days) ===")
    for app in flag_upcoming_deadlines(days_threshold=7):
        print(f"  [!] {app['title']} @ {app['company']} - due {app['deadline']}")


if __name__ == "__main__":
    main()
