"""Root-level conftest: shared fixtures for the entire test suite."""
import json
from pathlib import Path
from typing import Dict

import allure
import pytest
import yaml
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config import settings


# ── CLI hooks ────────────────────────────────────────────────────────────────

def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom CLI options."""
    parser.addoption(
        "--browser",
        action="store",
        default=settings.BROWSER,
        choices=["chromium", "firefox", "webkit"],
        help="Browser engine to run tests on",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run tests in headed mode (non-headless)",
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=settings.BASE_URL,
        help="Base URL for the application under test",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Deselect slow tests unless --run-slow is given."""
    if config.getoption("--run-slow"):
        return  # run everything
    skip_slow = pytest.mark.skip(reason="use --run-slow to include")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


# ── Playwright fixtures (session scoped)  ────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    """Start Playwright once per session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser_type(request: pytest.FixtureRequest, playwright_instance: Playwright):
    """Resolve the browser type from CLI option."""
    browser_name = request.config.getoption("--browser")
    browsers = {
        "chromium": playwright_instance.chromium,
        "firefox": playwright_instance.firefox,
        "webkit": playwright_instance.webkit,
    }
    return browsers[browser_name]


@pytest.fixture(scope="session")
def browser(browser_type) -> Browser:
    """Launch a browser once per session."""
    b = browser_type.launch(
        headless=settings.HEADLESS,
        slow_mo=settings.SLOW_MO,
        args=["--disable-blink-features=AutomationControlled"] if browser_type.name == "chromium" else None,
    )
    yield b
    b.close()


# ── Test-level fixtures ──────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def allure_environment(request: pytest.FixtureRequest) -> None:
    """Attach environment info to Allure report."""
    allure.dynamic.feature(request.node.parent.name if hasattr(request.node, "parent") else "Unknown")
    allure.dynamic.story(request.node.name)


@pytest.fixture()
def context(browser: Browser) -> BrowserContext:
    """Create a new browser context for each test (isolated storage/cookies)."""
    ctx = browser.new_context(
        viewport={"width": settings.VIEWPORT_WIDTH, "height": settings.VIEWPORT_HEIGHT},
        locale=settings.LOCALE,
        timezone_id=settings.TIMEZONE,
        ignore_https_errors=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext) -> Page:
    """Create a new page (tab) for each test."""
    p = context.new_page()
    p.set_default_timeout(settings.DEFAULT_TIMEOUT)
    p.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
    yield p
    p.close()


@pytest.fixture()
def base_url(request: pytest.FixtureRequest) -> str:
    """Get base URL from CLI option."""
    return request.config.getoption("--base-url")


# ── Test data helpers ────────────────────────────────────────────────────────

@pytest.fixture()
def test_data() -> Dict:
    """Load test data from JSON/YAML files in testdata/."""
    data = {}
    for filepath in settings.TESTDATA_DIR.glob("*"):
        if filepath.suffix in (".json",):
            with open(filepath, encoding="utf-8") as f:
                data[filepath.stem] = json.load(f)
        elif filepath.suffix in (".yaml", ".yml"):
            with open(filepath, encoding="utf-8") as f:
                data[filepath.stem] = yaml.safe_load(f)
    return data


# ── Screenshot on failure ────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Capture a screenshot when a test fails and attach to Allure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot_path = settings.SCREENSHOTS_DIR / f"{item.name}_{call.when}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            allure.attach.file(
                str(screenshot_path),
                name=f"Failure: {item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
