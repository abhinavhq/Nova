"""
nova/profile.py

Phase 5: Auto-fill from a saved profile.

Stores common personal details (name, email, phone, etc.) once, so Nova
can fill repetitive form fields without you retyping them every time.

IMPORTANT: this module only FILLS fields - it never submits anything.
Actual form submission still goes through NovaAgent's normal action loop,
which already pauses for confirmation on sensitive actions (submit, apply,
etc. - see agent.py's SENSITIVE_KEYWORDS). This module doesn't bypass that.
"""

import json
import os

DEFAULT_PROFILE_PATH = "nova_profile.json"


def load_profile(filepath: str = DEFAULT_PROFILE_PATH) -> dict:
    """Load saved profile details from a local JSON file."""
    if not os.path.exists(filepath):
        print(f"[profile] No profile found at {filepath} - returning empty profile.")
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


def save_profile(profile: dict, filepath: str = DEFAULT_PROFILE_PATH):
    """Save profile details to a local JSON file (kept out of git via .gitignore)."""
    with open(filepath, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"[profile] Saved profile to {filepath}")


def autofill_form(page, profile: dict) -> list[str]:
    """
    Scan the current page for form input elements, match each one to a
    profile field by its label/placeholder/name VALUE (not raw attribute
    syntax), and fill any matches.

    Only fills text-like inputs (text, email, tel, textarea, search, etc.)
    - checkboxes, radios, files, colors, and ranges are skipped since they
    can't be "filled" with text at all.

    This is deliberately deterministic (no LLM call) - form field matching
    doesn't need reasoning, just keyword matching, and being deterministic
    means it's predictable and auditable.

    Returns a list of short descriptions of what was filled/skipped, for
    logging. IMPORTANT: this only fills fields. It never clicks
    submit/continue - that decision is left to the caller, which should
    route through NovaAgent's confirmation gate (see agent.py
    SENSITIVE_KEYWORDS) if submission is involved.
    """
    import re
    from nova.perception import get_page_elements  # local import avoids circular import

    UNFILLABLE_TYPES = {"checkbox", "radio", "file", "color", "range", "submit", "button", "hidden"}

    filled = []
    elements = get_page_elements(page)

    for el in elements:
        if el.tag not in ("input", "textarea"):
            continue

        # extract the input's `type="..."` if present, to skip unfillable kinds
        type_match = re.search(r'type="([^"]*)"', el.attrs)
        input_type = type_match.group(1) if type_match else "text"
        if input_type in UNFILLABLE_TYPES:
            continue  # silently skip - not a real failure, just not applicable

        # match on ATTRIBUTE VALUES only (e.g. the "my-email" in name="my-email"),
        # not the raw "name=" syntax itself, which would false-match everything
        attr_values = " ".join(re.findall(r'="([^"]*)"', el.attrs))
        label_text = f"{el.text} {attr_values}"

        value = match_field_to_profile(label_text, profile)
        if value:
            try:
                el.locator.fill(str(value))
                filled.append(f"filled [{el.id}] ({label_text.strip()}) with '{value}'")
            except Exception as e:
                filled.append(f"failed to fill [{el.id}] ({label_text.strip()}): {e}")

    return filled


def match_field_to_profile(field_label: str, profile: dict) -> str | None:
    """
    Given a form field's label/placeholder text (e.g. "Email address",
    "Full Name", "Phone"), try to match it to a value in the profile.
    Simple keyword matching - good enough for common fields, not meant
    to be exhaustive.
    """
    label = field_label.lower()

    field_map = {
        "name": ["name", "full name", "your name"],
        "email": ["email", "e-mail"],
        "phone": ["phone", "mobile", "contact number"],
        "address": ["address", "street"],
        "city": ["city", "town"],
        "linkedin": ["linkedin"],
        "github": ["github"],
        "university": ["university", "school", "college"],
    }

    for profile_key, keywords in field_map.items():
        if any(kw in label for kw in keywords):
            return profile.get(profile_key)

    return None