"""
nova package

Exposes the core building blocks of Nova so they can be imported
directly from the package, e.g.:

    from nova import NovaBrowser

instead of:

    from nova.browser import NovaBrowser
"""

from nova.browser import NovaBrowser

__all__ = ["NovaBrowser"]