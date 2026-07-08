"""
nova/browser.py

Low-level "hands" for Nova. This module wraps Playwright and exposes
simple, reliable functions: launch a browser, navigate, click, type,
scroll, screenshot, and (soon) extract interactive elements.

No LLM logic lives here. This is pure browser automation.
"""

from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from pathlib import Path
import time


class NovaBrowser:
    def __init__(
        self,
        headless: bool = False,
        engine: str = "chromium",
        channel: str | None = None,
        executable_path: str | None = None,
    ):
        """
        headless=False is intentional for now — while we're building and
        debugging, you WANT to see what the browser is doing.
        Flip to True later once things are stable.

        engine: "chromium", "firefox", or "webkit" (which underlying
                Playwright driver to use).

        channel: for engine="chromium" only, use "chrome" or "msedge" to
                 launch your REAL installed Chrome/Edge instead of the
                 bundled Chromium.

        executable_path: point directly at a browser .exe — this is how
                 you launch Brave (or any other Chromium-based browser
                 Playwright doesn't know by name). Example on Windows:
                 r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
                 Using this also means Nova can access that browser's
                 existing profile/cookies/logins if you pass user_data_dir
                 via new_context (not wired up yet — future step).
        """
        self.headless = headless
        self.engine = engine
        self.channel = channel
        self.executable_path = executable_path
        self._playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def start(self):
        """Launch the browser and open a blank page."""
        self._playwright = sync_playwright().start()
        driver = getattr(self._playwright, self.engine)

        launch_kwargs = {"headless": self.headless}
        if self.channel:
            launch_kwargs["channel"] = self.channel  # e.g. "chrome", "msedge"
        if self.executable_path:
            launch_kwargs["executable_path"] = self.executable_path  # e.g. Brave

        self.browser = driver.launch(**launch_kwargs)
        context = self.browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        self.page = context.new_page()
        print(f"[NovaBrowser] Browser started (engine={self.engine}, "
              f"channel={self.channel}, executable_path={self.executable_path}).")

    def goto(self, url: str):
        """Navigate to a URL, waiting for the page to be mostly loaded."""
        print(f"[NovaBrowser] Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # small buffer for JS-heavy pages to settle
        self.page.wait_for_timeout(1000)
        self.dismiss_common_popups()

    def dismiss_common_popups(self):
        """
        Best-effort attempt to close cookie-consent banners and similar
        overlay popups that block interaction on most real-world sites.

        This is deliberately "fire and forget": if nothing matches, it does
        nothing and moves on quickly. It should never raise or block the
        agent loop — a missed popup just means perception might see it as
        an extra clickable element, which the LLM can still handle.
        """
        # common phrases used on consent/overlay buttons, checked in order
        common_labels = [
            "Accept all", "Accept All", "Accept Cookies", "I Accept",
            "Accept", "I Agree", "Agree", "Got it", "Ok", "OK",
            "Allow all", "Allow All", "Continue", "Close",
        ]
        for label in common_labels:
            try:
                btn = self.page.get_by_role("button", name=label, exact=False)
                if btn.count() > 0 and btn.first.is_visible(timeout=500):
                    btn.first.click(timeout=1000)
                    print(f"[NovaBrowser] Dismissed popup via button: '{label}'")
                    self.page.wait_for_timeout(300)
                    return  # one dismissal per nav is usually enough
            except Exception:
                # not present, not visible, or click failed - just move on
                continue

    def screenshot(self, path: str = "nova_screenshot.png"):
        """Save a screenshot of the current page state."""
        self.page.screenshot(path=path, full_page=False)
        print(f"[NovaBrowser] Screenshot saved to {path}")
        return path

    def click_selector(self, selector: str):
        """Click an element by CSS selector."""
        print(f"[NovaBrowser] Clicking selector: {selector}")
        self.page.click(selector, timeout=10000)

    def type_into(self, selector: str, text: str, press_enter: bool = False):
        """Type text into an input matched by CSS selector."""
        print(f"[NovaBrowser] Typing into {selector}: {text!r}")
        self.page.fill(selector, text)
        if press_enter:
            self.page.press(selector, "Enter")

    def scroll_down(self, amount_px: int = 800):
        self.page.mouse.wheel(0, amount_px)

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    def close(self):
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
        print("[NovaBrowser] Browser closed.")

    # Support "with NovaBrowser() as nb:" usage
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()