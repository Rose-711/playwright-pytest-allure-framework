from pages import BasePage
from playwright.sync_api import Page


class ExamplePage(BasePage):
    """Example Page Object for https://example.com."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = "https://example.com"

    # ── Locators ───────────────────────────────────────────
    @property
    def heading(self):
        return self.page.locator("h1")

    @property
    def paragraph(self):
        return self.page.locator("p")

    # ── Actions ────────────────────────────────────────────
    def open(self) -> None:
        """Navigate to the example page."""
        self.navigate(self.url)
        self.wait_for_load_state("networkidle")

    def get_heading_text(self) -> str:
        """Get the main heading text."""
        return self.heading.inner_text()

    def get_paragraph_text(self) -> str:
        """Get the first paragraph text."""
        return self.paragraph.first.inner_text()
