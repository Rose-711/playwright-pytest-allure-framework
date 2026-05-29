"""
==============================================================
  全局配置文件 —— 整个测试套件的"总控室"
==============================================================

  这个文件是 Pytest 的"钩子"入口，它主要干三件事：
  1. 管理浏览器的启动/关闭（不用每个测试自己管）
  2. 提供测试用的"现成工具"（fixture）
  3. 测试失败时自动截图

  注意：pytest-playwright 插件已经自带了 playwright、browser、
  context、page 这些 fixture。我们在这里覆盖（override）了
  一部分，让它们使用我们自己的配置（.env 文件里的设置）。
==============================================================
"""
import json
from pathlib import Path
from typing import Dict

import allure
import pytest
import yaml
from playwright.sync_api import Browser, BrowserContext, Page

from config import settings  # 从 .env 文件加载的设置


# ═══════════════════════════════════════════════════════════════
#  一、测试收集阶段的钩子
#  作用：在 Pytest 收集到所有测试之后、真正运行之前执行
# ═══════════════════════════════════════════════════════════════

def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """
    自动跳过标记为 slow 的测试，除非用户传了 --run-slow 参数。

    为什么要做这个：
      有些测试跑得特别慢（比如加载大文件、等待超时），
      平时不想跑它们，但偶尔又想跑一下，于是加个开关控制。

    用法：
      pytest                    # 跳过 slow 测试
      pytest --run-slow         # 也跑 slow 测试
    """
    # 用户在命令行传了 --run-slow 吗？传了就不跳过
    if config.getoption("--run-slow", default=False):
        return

    # 没传 —— 给每个 slow 测试打上"跳过"标记
    skip_slow = pytest.mark.skip(reason="use --run-slow to include")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


# ═══════════════════════════════════════════════════════════════
#  二、浏览器 fixture
#  作用：帮每个测试准备好浏览器，用完自动关闭
#
#  ⭐ fixture 是 Pytest 最核心的概念
#  简单理解：就是一个"自动的准备工作"
#  你只需要在测试函数里写参数名，Pytest 就会自动调用对应的函数
#
#  例如：def test_something(page):
#          page.goto("https://...")
#  你不需要自己 new_page()，也不用关，Pytest 全包了
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def browser(playwright, browser_name) -> Browser:
    """
    启动浏览器 —— 整个测试过程只启动一次。

    scope="session" 的意思是"会话级别"：
      整个测试跑完只会调用一次这个函数（而不是每个测试都启动一次浏览器）
      这样可以节省大量时间。

    我们的配置：
      - 默认使用系统安装的 Chrome（channel="chrome"）
      - 是否显示窗口看 HEADLESS 配置
      - 加了反自动化检测参数（防止网站识别出是机器操作）
    """
    # playwright 对象包含了 chromium / firefox / webkit 三种浏览器
    # browser_name 由 pytest-playwright 自动从 --browser 参数获取
    browser_type = getattr(playwright, browser_name)

    launch_kwargs: dict = {
        "headless": settings.HEADLESS,     # 无头模式（不显示窗口）
        "slow_mo": settings.SLOW_MO,       # 每一步操作之间的延迟（毫秒）
    }

    # 如果用 Chromium，额外设置：
    if browser_name == "chromium":
        # 使用系统已安装的 Chrome（不用 Playwright 自带的）
        launch_kwargs["channel"] = "chrome"
        # 这个参数可以防止网站识别出是 Playwright 在操作
        launch_kwargs["args"] = ["--disable-blink-features=AutomationControlled"]

    b = browser_type.launch(**launch_kwargs)
    yield b  # ← 关键：yield 把浏览器"交给"测试用
    b.close()  # ← 测试全部跑完后关闭浏览器


@pytest.fixture()
def context(browser: Browser) -> BrowserContext:
    """
    创建浏览器上下文（相当于 Chrome 里一个"无痕窗口"）。

    每个测试都会拿到一个全新的上下文，好处是：
      - cookie、缓存、storage 互不干扰
      - 上一个测试的登录状态不会影响下一个

    ⚠️ scope 没写，默认是 function 级别（每个测试各调一次）
    """
    ctx = browser.new_context(
        # 设置窗口大小
        viewport={"width": settings.VIEWPORT_WIDTH, "height": settings.VIEWPORT_HEIGHT},
        locale=settings.LOCALE,            # 浏览器语言（zh-CN）
        timezone_id=settings.TIMEZONE,     # 时区
        ignore_https_errors=True,          # 忽略 HTTPS 证书错误
    )
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext) -> Page:
    """
    创建一个新的标签页。

    对 Playwright 来说，"page" 就是浏览器的"标签页"。
    绝大部分测试操作都在 page 上进行：点击、输入、截图等。
    """
    p = context.new_page()

    # 设置超时时间（单位：毫秒）
    # 如果页面加载超过这个时间，测试会被判失败
    p.set_default_timeout(settings.DEFAULT_TIMEOUT)
    p.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)

    yield p
    p.close()


# ═══════════════════════════════════════════════════════════════
#  三、Allure 报告集成
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def allure_environment(request: pytest.FixtureRequest) -> None:
    """
    自动给每个测试添加 Allure 报告的 feature/story 标签。

    autouse=True 的意思是"每个测试自动生效"，不用你手动写。

    效果：
      在 Allure 报告里，测试会按 feature → story 分组展示，
      看起来更清晰。
    """
    # 把测试类名作为 feature，测试函数名作为 story
    parent = request.node.parent
    allure.dynamic.feature(getattr(parent, "name", "Unknown"))
    allure.dynamic.story(request.node.name)


# ═══════════════════════════════════════════════════════════════
#  四、测试数据加载器
# ═══════════════════════════════════════════════════════════════

@pytest.fixture()
def test_data() -> Dict:
    """
    从 testdata/ 文件夹读取 JSON/YAML 测试数据。

    使用方式（在测试函数里加 test_data 参数）：
      def test_login(test_data):
          users = test_data["valid_users"]
          # users 就是 testdata/test_data.json 里的内容

    支持格式：.json、.yaml、.yml
    会自动加载 testdata/ 下所有匹配的文件。
    """
    data = {}
    for filepath in settings.TESTDATA_DIR.glob("*"):
        if filepath.suffix in (".json",):
            with open(filepath, encoding="utf-8") as f:
                data[filepath.stem] = json.load(f)
        elif filepath.suffix in (".yaml", ".yml"):
            with open(filepath, encoding="utf-8") as f:
                data[filepath.stem] = yaml.safe_load(f)
    return data


# ═══════════════════════════════════════════════════════════════
#  五、失败自动截图
#  最实用的功能之一！
#  测试挂了不用慌，框架会自动截一张当时的页面图片，
#  并且附到 Allure 报告里。
# ═══════════════════════════════════════════════════════════════

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """
    测试执行完毕后自动调用。
    如果测试失败了，就给当时的页面拍张照。

    tryfirst=True 表示这个钩子优先执行。
    hookwrapper=True 允许我们在"包裹"原函数的前后都执行代码。
    """
    outcome = yield
    report = outcome.get_result()

    # report.when 有三种值：setup / call / teardown
    # 我们只关心 call（测试实际执行阶段）的失败
    if report.when == "call" and report.failed:
        # 从测试的参数里找到 page 对象
        page = item.funcargs.get("page")
        if page:
            # 截图保存到 screenshots/ 目录
            screenshot_path = settings.SCREENSHOTS_DIR / f"{item.name}_{call.when}.png"
            page.screenshot(path=screenshot_path, full_page=True)

            # 把截图附加到 Allure 报告里
            allure.attach.file(
                str(screenshot_path),
                name=f"Failure: {item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
