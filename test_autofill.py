"""
test_autofill.py

Sanity check for the last Phase 5 piece: auto-fill form fields from a
saved profile, and ALWAYS confirm before submitting anything.

Uses httpbin.org/forms/post - a public, stable test form built exactly
for this kind of testing (customer name, telephone, email fields).
"""

from nova import NovaBrowser
from nova.profile import save_profile, load_profile, autofill_form


def main():
    # 1. Save a sample profile (only needs to be done once in real usage)
    sample_profile = {
        "name": "Abhinav Yadav",
        "email": "abhinav.example@example.com",
        "phone": "+91-9999999999",
    }
    save_profile(sample_profile)

    # 2. Load it back (proves persistence works)
    profile = load_profile()
    print(f"Loaded profile: {profile}")

    # 3. Auto-fill a real form - using a self-contained test form (no
    # external site dependency, and field names are realistic so we can
    # properly verify the matching logic)
    TEST_FORM_HTML = """
    <html><body>
      <h1>Sample Application Form</h1>
      <form>
        <label>Full Name: <input type="text" name="full_name" placeholder="Your full name"></label><br>
        <label>Email: <input type="email" name="email" placeholder="you@example.com"></label><br>
        <label>Phone Number: <input type="tel" name="phone" placeholder="Phone"></label><br>
        <label>Message: <textarea name="message" placeholder="Comments"></textarea></label><br>
        <label>Subscribe: <input type="checkbox" name="subscribe"></label><br>
        <button type="submit">Submit Application</button>
      </form>
    </body></html>
    """

    with NovaBrowser(headless=False) as nb:
        nb.page.set_content(TEST_FORM_HTML)

        filled = autofill_form(nb.page, profile)
        print("\n=== AUTOFILL RESULTS ===")
        for entry in filled:
            print(f"  {entry}")

        nb.screenshot("phase5_autofill_result.png")

        # 4. Confirmation before ANY submission - autofill_form never
        # submits on its own, this is a manual explicit gate
        print("\nForm has been filled but NOT submitted.")
        answer = input("Submit the form now? [y/N]: ").strip().lower()
        if answer == "y":
            nb.page.get_by_role("button", name="Submit Application").click()
            print("Submitted.")
        else:
            print("Skipped submission - form left filled, unsubmitted.")

        nb.page.wait_for_timeout(2000)


if __name__ == "__main__":
    main()