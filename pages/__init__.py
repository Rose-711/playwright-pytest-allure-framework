from pathlib import Path

from playwright.sync_api import Locator, Page


class BasePage:
    """Base class for all Page Objects providing common interaction methods."""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = 30000

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, url: str) -> None:
        """Navigate to a URL and wait for the page to load."""
        self.page.goto(url, wait_until="load")

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def get_title(self) -> str:
        """Return the page title."""
        return self.page.title()

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload(wait_until="load")

    # ── Waiting ───────────────────────────────────────────────────────────────

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int | None = None) -> Locator:
        """Wait for an element matching the selector to reach the expected state."""
        self.page.wait_for_selector(selector, state=state, timeout=timeout or self.timeout)
        return self.page.locator(selector)

    def wait_for_url(self, url_pattern: str, timeout: int | None = None) -> None:
        """Wait until the current URL matches the given pattern."""
        self.page.wait_for_url(url_pattern, timeout=timeout or self.timeout)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        """Wait for the page to reach the given load state."""
        self.page.wait_for_load_state(state)

    # ── Click ─────────────────────────────────────────────────────────────────

    def click(self, selector: str, *, force: bool = False, timeout: int | None = None) -> None:
        """Click the element matching the selector."""
        self.page.click(selector, force=force, timeout=timeout or self.timeout)

    def click_by_text(self, text: str, *, exact: bool = True) -> None:
        """Click an element by its text content."""
        self.page.get_by_text(text, exact=exact).click()

    def double_click(self, selector: str) -> None:
        """Double-click the element matching the selector."""
        self.page.dblclick(selector, timeout=self.timeout)

    # ── Input ─────────────────────────────────────────────────────────────────

    def fill(self, selector: str, text: str, *, timeout: int | None = None) -> None:
        """Clear the input field and type the given text."""
        self.page.fill(selector, text, timeout=timeout or self.timeout)

    def type_text(self, selector: str, text: str, *, delay: int = 50) -> None:
        """Type text into the input field character by character."""
        self.page.type(selector, text, delay=delay)

    def clear(self, selector: str) -> None:
        """Clear the input field."""
        self.page.fill(selector, "")

    def press_key(self, key: str) -> None:
        """Press a keyboard key (Enter, Tab, Escape, etc.)."""
        self.page.keyboard.press(key)

    # ── Check / Radio / Select ────────────────────────────────────────────────

    def check(self, selector: str) -> None:
        """Check a checkbox or radio button."""
        self.page.check(selector)

    def uncheck(self, selector: str) -> None:
        """Uncheck a checkbox."""
        self.page.uncheck(selector)

    def select_option(self, selector: str, value: str | list[str]) -> None:
        """Select an option from a <select> element by value."""
        self.page.select_option(selector, value)

    def select_option_by_label(self, selector: str, label: str) -> None:
        """Select an option from a <select> element by visible label."""
        self.page.select_option(selector, label=label)

    # ── Text / Attributes ─────────────────────────────────────────────────────

    def get_text(self, selector: str) -> str:
        """Get the inner text of an element."""
        return self.page.inner_text(selector)

    def get_attribute(self, selector: str, attr: str) -> str | None:
        """Get an attribute value from the element."""
        return self.page.get_attribute(selector, attr)

    def get_value(self, selector: str) -> str:
        """Get the value attribute of an input element."""
        return self.page.input_value(selector)

    # ── Visibility ────────────────────────────────────────────────────────────

    def is_visible(self, selector: str, timeout: int | None = None) -> bool:
        """Check if the element is visible."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout or 5000)
            return True
        except Exception:
            return False

    def is_hidden(self, selector: str, timeout: int | None = None) -> bool:
        """Check if the element is hidden."""
        try:
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout or 5000)
            return True
        except Exception:
            return False

    def is_enabled(self, selector: str) -> bool:
        """Check if the element is enabled."""
        return self.page.is_enabled(selector)

    # ── Screenshot ────────────────────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot", full_page: bool = True) -> Path:
        """Take a screenshot and save it to the screenshots directory."""
        from config.settings import settings
        path = settings.SCREENSHOTS_DIR / f"{name}.png"
        self.page.screenshot(path=path, full_page=full_page)
        return path

    # ── Scroll ────────────────────────────────────────────────────────────────

    def scroll_into_view(self, selector: str) -> None:
        """Scroll the element into view."""
        self.page.locator(selector).scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        """Scroll to the top of the page."""
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # ── JavaScript ────────────────────────────────────────────────────────────

    def execute_script(self, script: str, *args) -> any:
        """Execute JavaScript on the page."""
        return self.page.evaluate(script, *args)

    # ── Alerts / Dialogs ──────────────────────────────────────────────────────

    def accept_alert(self) -> None:
        """Accept a browser dialog (alert, confirm, prompt)."""
        self.page.once("dialog", lambda dialog: dialog.accept())

    def dismiss_alert(self) -> None:
        """Dismiss a browser dialog."""
        self.page.once("dialog", lambda dialog: dialog.dismiss())

    # ── Frames ────────────────────────────────────────────────────────────────

    def switch_to_frame(self, selector: str) -> None:
        """Switch to an iframe by selector."""
        frame = self.page.frame_locator(selector)
        if frame is None:
            raise ValueError(f"Frame not found: {selector}")

    def switch_to_main(self) -> None:
        """Switch back to the main page (out of any frame)."""
        # Playwright handles frames through frame_locator; no explicit switch needed
        pass

    # ── Cookies ───────────────────────────────────────────────────────────────

    def set_cookie(self, name: str, value: str, url: str | None = None) -> None:
        """Set a browser cookie."""
        self.page.context.add_cookies([{"name": name, "value": value, "url": url or self.get_current_url()}])

    def clear_cookies(self) -> None:
        """Clear all browser cookies."""
        self.page.context.clear_cookies()
