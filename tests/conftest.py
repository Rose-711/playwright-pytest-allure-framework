"""Test-level fixtures specific to the tests/ directory."""
import pytest
from playwright.sync_api import Page


@pytest.fixture()
def example_page(page: Page):
    """Create an ExamplePage instance."""
    from pages.example_page import ExamplePage
    ep = ExamplePage(page)
    ep.open()
    return ep
