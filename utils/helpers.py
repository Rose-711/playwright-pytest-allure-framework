"""General-purpose helper functions."""
import json
import random
import string
import time
from pathlib import Path
from typing import Any


def generate_random_string(length: int = 10) -> str:
    """Generate a random alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email(domain: str = "test.com") -> str:
    """Generate a random email for testing."""
    return f"test_{generate_random_string(8).lower()}@{domain}"


def generate_random_phone() -> str:
    """Generate a random 11-digit Chinese phone number."""
    prefixes = ["13", "15", "17", "18", "19"]
    return random.choice(prefixes) + "".join(random.choices(string.digits, k=9))


def read_json(filepath: str | Path) -> dict:
    """Read a JSON file and return its contents."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath: str | Path, data: Any) -> None:
    """Write data to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def current_timestamp() -> str:
    """Return the current timestamp string: YYYY-MM-DD_HH-MM-SS."""
    return time.strftime("%Y-%m-%d_%H-%M-%S")


def retry(func: callable, retries: int = 3, delay: float = 1.0, *args, **kwargs) -> Any:
    """Retry a function call with exponential backoff."""
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries:
                time.sleep(delay * (2 ** (attempt - 1)))
    raise last_exception  # type: ignore
