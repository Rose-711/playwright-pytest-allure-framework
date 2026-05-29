"""Allure reporting utilities."""
import allure


def attach_screenshot(page, name: str = "Screenshot") -> None:
    """Attach a screenshot to the Allure report."""
    allure.attach(
        page.screenshot(full_page=True),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def attach_html(name: str, html: str) -> None:
    """Attach HTML content to the Allure report."""
    allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)


def attach_text(name: str, text: str) -> None:
    """Attach text content to the Allure report."""
    allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_json(name: str, data: dict | list) -> None:
    """Attach JSON data to the Allure report."""
    import json
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def step(name: str):
    """Decorator / context manager for Allure steps.

    Usage as decorator:
        @step("User logs in")
        def login(): ...

    Usage as context manager:
        with step("Navigate to page"):
            page.goto(url)
    """
    return allure.step(name)
