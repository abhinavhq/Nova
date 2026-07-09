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

__all__ = [
    "NovaBrowser",
    "get_page_elements",
    "get_page_summary",
    "format_elements_for_llm",
    "NovaAgent",
    "NovaPlanner",
    "NovaOrchestrator",
]