"""
nova package

Exposes the core building blocks of Nova so they can be imported
directly from the package, e.g.:

    from nova import NovaBrowser

instead of:

    from nova.browser import NovaBrowser
"""

from nova.browser import NovaBrowser
from nova.perception import get_page_elements, get_page_summary, format_elements_for_llm
from nova.agent import NovaAgent
from nova.planner import NovaPlanner, NovaOrchestrator
from nova.extraction import extract_structured_data
from nova.export import save_to_xlsx
from nova.compare import compare_across_sources
from nova.summarize import summarize_page
from nova.pdf_handler import download_pdf, extract_pdf_text, read_pdf_from_url
from nova.generate import generate_cover_letter, draft_email_from_content, generate_itinerary
from nova.profile import load_profile, save_profile, match_field_to_profile, autofill_form
from nova.tracker import add_application, update_status, list_applications, flag_upcoming_deadlines
from nova.price_tracker import record_price, get_price_history, list_tracked_products

__all__ = [
    "NovaBrowser",
    "get_page_elements",
    "get_page_summary",
    "format_elements_for_llm",
    "NovaAgent",
    "NovaPlanner",
    "NovaOrchestrator",
    "extract_structured_data",
    "save_to_xlsx",
    "compare_across_sources",
    "summarize_page",
    "download_pdf",
    "extract_pdf_text",
    "read_pdf_from_url",
    "generate_cover_letter",
    "draft_email_from_content",
    "generate_itinerary",
    "load_profile",
    "save_profile",
    "match_field_to_profile",
    "autofill_form",
    "add_application",
    "update_status",
    "list_applications",
    "flag_upcoming_deadlines",
    "record_price",
    "get_price_history",
    "list_tracked_products",
]