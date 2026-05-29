"""Test data loading utilities."""
import json
from pathlib import Path
from typing import Any

import yaml

from config.settings import settings


def load_test_data(filename: str) -> dict[str, Any]:
    """Load test data from a JSON or YAML file in testdata/."""
    filepath = settings.TESTDATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Test data file not found: {filepath}")

    suffix = filepath.suffix.lower()
    with open(filepath, encoding="utf-8") as f:
        if suffix == ".json":
            return json.load(f)
        elif suffix in (".yaml", ".yml"):
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")


def parametrize_from_json(filename: str, key: str | None = None) -> list[tuple]:
    """Load parametrized test data from a JSON file.

    Usage:
        @pytest.mark.parametrize("username, password",
            parametrize_from_json("login_data.json", "valid_users"))
    """
    data = load_test_data(filename)
    if key:
        data = data[key]
    return [tuple(item.values()) if isinstance(item, dict) else (item,) for item in data]
