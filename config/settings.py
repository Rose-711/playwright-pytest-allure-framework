import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Application settings loaded from environment variables / .env file."""

    # ── Browser ──────────────────────────────────────────────
    BROWSER: str = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))
    VIEWPORT_WIDTH: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    VIEWPORT_HEIGHT: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))
    LOCALE: str = os.getenv("LOCALE", "zh-CN")
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Shanghai")

    # ── Timeouts (ms) ────────────────────────────────────────
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))

    # ── Test data ────────────────────────────────────────────
    BASE_URL: str = os.getenv("BASE_URL", "https://example.com")
    USERNAME: str = os.getenv("TEST_USERNAME", "")
    PASSWORD: str = os.getenv("TEST_PASSWORD", "")

    # ── Directories ──────────────────────────────────────────
    SCREENSHOTS_DIR: Path = ROOT_DIR / "screenshots"
    REPORTS_DIR: Path = ROOT_DIR / "reports"
    TESTDATA_DIR: Path = ROOT_DIR / "testdata"

    # ── Retry ────────────────────────────────────────────────
    RETRY_TIMES: int = int(os.getenv("RETRY_TIMES", "0"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "5"))

    def __getattr__(self, name: str) -> str:
        val = os.getenv(name)
        if val is not None:
            return val
        raise AttributeError(f"Settings has no attribute '{name}'")


settings = Settings()
