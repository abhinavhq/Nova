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
]