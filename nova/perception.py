"""
nova/perception.py

Turns the current page into a compact, numbered list of interactive
elements the LLM can reason about — instead of feeding it raw HTML
(too big, too noisy, too easy to hallucinate selectors against).

The core idea: walk visible interactive elements (buttons, links,
inputs, selects, textareas), assign each a short numeric ID, and
return both:
  - a human/LLM-readable text summary
  - a lookup table mapping ID -> Playwright locator

The agent (Step 3) will show the LLM the text summary, get back a
decision like {"action": "click", "id": 4}, and use the lookup table
to actually perform it.
"""

from playwright.sync_api import Page
from dataclasses import dataclass


# Elements we care about. Deliberately conservative for now —
# we can expand this as we hit real-world pages that need more.
INTERACTIVE_SELECTOR = ", ".join([
    "a[href]",
    "button",
    "input:not([type=hidden])",
    "select",
    "textarea",
    "[role=button]",
    "[role=link]",
    "[role=textbox]",
    "[onclick]",
])


@dataclass
class ElementInfo:
    id: int
    tag: str
    text: str
    attrs: str
    locator: object  # Playwright Locator, kept for later action execution


def _describe_element(tag: str, el_handle) -> tuple[str, str]:
    """Return (visible_text, useful_attrs) for a single element handle."""
    text = (el_handle.inner_text() or "").strip()
    if not text:
        # fall back to attributes that hint at purpose
        text = (
            el_handle.get_attribute("aria-label")
            or el_handle.get_attribute("placeholder")
            or el_handle.get_attribute("value")
            or el_handle.get_attribute("title")
            or ""
        ).strip()
    text = text[:80]  # keep it short, avoid blowing up token budget

    attrs = []
    for attr in ("type", "placeholder", "name", "href"):
        val = el_handle.get_attribute(attr)
        if val:
            val = val[:60]
            attrs.append(f'{attr}="{val}"')
    return text, " ".join(attrs)


def get_page_elements(page: Page, max_elements: int = 60) -> list[ElementInfo]:
    """
    Scan the page for visible, interactive elements and return a list
    of ElementInfo, each with a stable numeric ID for this snapshot.
    """
    locator = page.locator(INTERACTIVE_SELECTOR)
    count = locator.count()

    elements: list[ElementInfo] = []
    next_id = 1

    for i in range(count):
        if next_id > max_elements:
            break

        el = locator.nth(i)
        try:
            if not el.is_visible():
                continue
        except Exception:
            continue

        try:
            tag = el.evaluate("el => el.tagName.toLowerCase()")
            handle = el.element_handle()
            if handle is None:
                continue
            text, attrs = _describe_element(tag, el)
        except Exception:
            continue

        # skip elements with no text and no useful attrs — usually junk
        if not text and not attrs:
            continue

        elements.append(ElementInfo(id=next_id, tag=tag, text=text, attrs=attrs, locator=el))
        next_id += 1

    return elements


def format_elements_for_llm(elements: list[ElementInfo]) -> str:
    """Turn ElementInfo list into a compact text block for the LLM prompt."""
    lines = []
    for e in elements:
        label = f'"{e.text}"' if e.text else ""
        attr_part = f" {e.attrs}" if e.attrs else ""
        lines.append(f"[{e.id}] <{e.tag}> {label}{attr_part}".strip())
    return "\n".join(lines)


def get_page_full_text(page: Page, max_chars: int = 6000) -> str:
    """
    Grab a larger chunk of the page's visible text than get_page_text_context
    provides. Used for DATA EXTRACTION tasks (Phase 3), where the LLM needs
    enough raw content to pull out structured fields (titles, prices,
    ratings, etc.) - not just enough to know where it landed.
    """
    try:
        body_text = page.locator("body").inner_text()
        return " ".join(body_text.split())[:max_chars]
    except Exception:
        return "(no readable text content found)"


def get_page_text_context(page: Page, max_chars: int = 300) -> str:
    """
    Grab a short snippet of the page's main visible heading/text so the
    LLM can tell WHERE it landed (e.g. "Artificial intelligence" article),
    not just what's clickable. This is what lets the agent recognize
    success instead of repeating an action forever.
    """
    try:
        # prefer the first visible h1, fall back to page title area
        heading = page.locator("h1").first
        heading_text = heading.inner_text().strip() if heading.count() > 0 else ""
    except Exception:
        heading_text = ""

    try:
        body_text = page.locator("body").inner_text()
        body_snippet = " ".join(body_text.split())[:max_chars]
    except Exception:
        body_snippet = ""

    parts = []
    if heading_text:
        parts.append(f"main heading: {heading_text}")
    if body_snippet:
        parts.append(f"visible text snippet: {body_snippet}")
    return "\n".join(parts) if parts else "(no readable text content found)"


def get_page_summary(page: Page) -> tuple[str, list[ElementInfo]]:
    """
    Convenience wrapper: returns (text_summary, elements) for the current
    page, ready to hand to the LLM and later map an ID back to an action.

    text_summary now includes a short text-context block ahead of the
    element list, so the LLM can tell what page it's actually on.
    """
    elements = get_page_elements(page)
    element_summary = format_elements_for_llm(elements)
    text_context = get_page_text_context(page)
    summary = f"{text_context}\n\ninteractive elements:\n{element_summary}"
    return summary, elements