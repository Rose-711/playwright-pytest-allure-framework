"""
==============================================================
  配置管理模块 —— 从 .env 文件加载配置
==============================================================

  为什么需要这个文件？
    测试中用到的各种参数（浏览器类型、超时时间、目标网址等），
    如果直接写在代码里，每次改都要改代码。

    所以我们把它们放到 .env 文件里，
    这个模块负责读取 .env 文件并提供给其他模块使用。

  使用方法：
    from config import settings
    print(settings.BASE_URL)       # 获取目标网址
    print(settings.HEADLESS)      # 是否使用无头模式

  修改配置：
    复制 .env.example 为 .env，然后修改里面的值就行。
==============================================================
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# ── 加载 .env 文件 ─────────────────────────────────────────
# python-dotenv 会读取项目根目录的 .env 文件，
# 把里面的 KEY=VALUE 设置到环境变量里。
# 如果没有 .env 文件，就使用代码里写的默认值。
load_dotenv()

# 项目根目录路径
# __file__ 是当前文件 (settings.py) 的路径
# .parent.parent 就是项目根目录
# 比如：D:/VibeCoding/automation-test-framework/
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """配置管理类。

    所有配置项都定义为类属性，优先级：
      1. .env 文件中设置的值（最高优先级）
      2. 代码里写的默认值（最低优先级）

    使用方式：
      settings = Settings()
      settings.BROWSER  # 获取浏览器类型
    """

    # ═══════════════════════════════════════════════════════════
    #  浏览器配置
    # ═══════════════════════════════════════════════════════════

    # 浏览器类型：chromium（Chrome）| firefox | webkit（Safari）
    BROWSER: str = os.getenv("BROWSER", "chromium")

    # 是否使用"无头模式"（不显示浏览器窗口）
    # 设为 true 时，浏览器在后台运行，不弹窗口
    # CI（持续集成）环境下通常设为 true
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # 操作之间的延迟（毫秒）
    # 设为 100 的话，每次点击/输入之间会等 100ms
    # 看起来更像真人在操作，但测试会变慢
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # 浏览器窗口大小
    VIEWPORT_WIDTH: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    VIEWPORT_HEIGHT: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))

    # 浏览器语言和时区
    LOCALE: str = os.getenv("LOCALE", "zh-CN")
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Shanghai")

    # ═══════════════════════════════════════════════════════════
    #  超时配置（单位：毫秒）
    # ═══════════════════════════════════════════════════════════

    # 查找元素、点击、输入等操作的超时
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))  # 30秒

    # 页面加载的超时（打开网址时等待）
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))  # 60秒

    # ═══════════════════════════════════════════════════════════
    #  测试目标配置
    # ═══════════════════════════════════════════════════════════

    # 被测应用的网址
    BASE_URL: str = os.getenv("BASE_URL", "https://example.com")

    # 测试用的账号密码（敏感信息放 .env，不放代码里）
    USERNAME: str = os.getenv("TEST_USERNAME", "")
    PASSWORD: str = os.getenv("TEST_PASSWORD", "")

    # ═══════════════════════════════════════════════════════════
    #  目录配置
    # ═══════════════════════════════════════════════════════════

    # 截图保存目录
    SCREENSHOTS_DIR: Path = ROOT_DIR / "screenshots"
    # Allure 报告输出目录
    REPORTS_DIR: Path = ROOT_DIR / "reports"
    # 测试数据文件目录
    TESTDATA_DIR: Path = ROOT_DIR / "testdata"

    # ═══════════════════════════════════════════════════════════
    #  失败重试配置
    # ═══════════════════════════════════════════════════════════

    # 测试失败后重试次数（0 = 不重试）
    RETRY_TIMES: int = int(os.getenv("RETRY_TIMES", "0"))
    # 重试之间的等待时间（秒）
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "5"))

    def __getattr__(self, name: str) -> str:
        """
        支持动态获取环境变量。

        如果你在 .env 里写了一个新的变量，
        比如 MY_TOKEN=abc123，
        即使 Settings 类没有定义 MY_TOKEN 属性，
        也可以通过 settings.MY_TOKEN 获取到。
        """
        val = os.getenv(name)
        if val is not None:
            return val
        raise AttributeError(f"Settings has no attribute '{name}'")


# ── 导出单例 ───────────────────────────────────────────────
# 在其他模块中这样使用：
#   from config import settings
#   settings.BROWSER
settings = Settings()
