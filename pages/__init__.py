"""
==============================================================
  BasePage —— 所有页面对象的"祖宗类"
==============================================================

  什么是 Page Object（页面对象）？
  就是把一个网页上的操作，封装成一个 Python 类。

  比如百度首页有搜索框和搜索按钮，我们就写一个 BaiduPage：
    class BaiduPage(BasePage):
        def search(self, keyword):
            self.fill("#kw", keyword)   # 输入关键词
            self.click("#su")           # 点搜索按钮

  好处：
    1. 如果百度改了搜索框的 ID，只需要改 BaiduPage 一个地方
    2. 测试代码读起来像人话：baidu_page.search("Python")
    3. 不用在每个测试里重复写 fill / click

  BasePage 就是所有页面对象的"基类"，
  把最常用的浏览器操作都封装好，子类直接继承使用。
==============================================================
"""
from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page


class BasePage:
    """所有 Page Object 的基类，提供通用的页面操作方法。"""

    def __init__(self, page: Page):
        """
        初始化页面对象。

        参数：
          page: Playwright 的 Page 对象（代表一个浏览器标签页）
        """
        self.page = page
        # 默认超时时间 30 秒（单位：毫秒）
        # 如果某个操作没在时间内完成，Pytest 会报超时错误
        self.timeout = 30000

    # ═══════════════════════════════════════════════════════════
    #  一、页面导航
    # ═══════════════════════════════════════════════════════════

    def navigate(self, url: str) -> None:
        """
        打开一个网址，并等待页面完全加载。

        参数：
          url: 要打开的网址，比如 "https://www.baidu.com"

        wait_until="load" 表示等待所有资源加载完毕。
        如果网络慢，这个操作可能会超时。
        """
        self.page.goto(url, wait_until="load")

    def get_current_url(self) -> str:
        """获取当前页面的网址。"""
        return self.page.url

    def get_title(self) -> str:
        """获取网页的标题（浏览器标签栏上显示的文字）。"""
        return self.page.title()

    def reload(self) -> None:
        """刷新当前页面。"""
        self.page.reload(wait_until="load")

    # ═══════════════════════════════════════════════════════════
    #  二、等待操作
    #  网页加载需要时间，所以"等待"是自动化测试最重要的操作之一
    # ═══════════════════════════════════════════════════════════

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int | None = None) -> Locator:
        """
        等待页面上的某个元素出现，并返回这个元素。

        参数：
          selector: CSS 选择器，比如 "#kw" 表示 id="kw" 的元素
          state: 等待的状态，可以是：
                 "attached" — 元素出现在 DOM 中
                 "visible"  — 元素在页面上可见（默认）
                 "hidden"   — 元素隐藏
          timeout: 超时时间（毫秒），不传就用默认的 30 秒

        返回：
          匹配的元素对象（Playwright 的 Locator）
        """
        self.page.wait_for_selector(selector, state=state, timeout=timeout or self.timeout)
        return self.page.locator(selector)

    def wait_for_url(self, url_pattern: str, timeout: int | None = None) -> None:
        """
        等待页面跳转到指定的网址。

        常用于：点击按钮后，页面 URL 会变化，等变化完成再继续。

        参数：
          url_pattern: 可以传完整 URL 或正则模式，如 "**/login"
          timeout: 超时时间（毫秒）
        """
        self.page.wait_for_url(url_pattern, timeout=timeout or self.timeout)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        """
        等待页面进入指定的加载状态。

        参数：
          state: 加载状态，常用的是：
                 "load"       — 页面基本加载完毕
                 "networkidle" — 网络请求都结束了（更保险，但也更慢）
        """
        self.page.wait_for_load_state(state)

    # ═══════════════════════════════════════════════════════════
    #  三、点击操作
    # ═══════════════════════════════════════════════════════════

    def click(self, selector: str, *, force: bool = False, timeout: int | None = None) -> None:
        """
        点击页面上的某个元素。

        参数：
          selector: 要点击的元素的选择器，如 "#su"、"button"
          force: True 的话，就算元素被遮挡也强制点击
          timeout: 超时时间（毫秒）
        """
        self.page.click(selector, force=force, timeout=timeout or self.timeout)

    def click_by_text(self, text: str, *, exact: bool = True) -> None:
        """
        通过文字内容来点击（不用写选择器）。

        例如：click_by_text("登录") 会自动找到页面上写着"登录"的按钮。

        参数：
          text: 要点击的文本
          exact: 是否完全匹配（True）还是部分匹配（False）
        """
        self.page.get_by_text(text, exact=exact).click()

    def double_click(self, selector: str) -> None:
        """双击页面上的某个元素。"""
        self.page.dblclick(selector, timeout=self.timeout)

    # ═══════════════════════════════════════════════════════════
    #  四、输入操作
    # ═══════════════════════════════════════════════════════════

    def fill(self, selector: str, text: str, *, timeout: int | None = None) -> None:
        """
        在输入框里输入文字。

        这个方法会先清空输入框，再输入新内容。

        参数：
          selector: 输入框的选择器，如 "#username"
          text: 要输入的文字
          timeout: 超时时间（毫秒）
        """
        self.page.fill(selector, text, timeout=timeout or self.timeout)

    def type_text(self, selector: str, text: str, *, delay: int = 50) -> None:
        """
        模拟人打字一样逐字输入（每个字之间有小延迟）。

        某些网站会检测是否是"真人"输入，
        用 fill() 是瞬间输入，可能被识别为机器。
        用 type_text() 更像真人操作。
        """
        self.page.type(selector, text, delay=delay)

    def clear(self, selector: str) -> None:
        """清空输入框里的内容。"""
        self.page.fill(selector, "")

    def press_key(self, key: str) -> None:
        """
        模拟键盘按键。

        常用的 key 值：
          "Enter"  — 回车
          "Tab"    — 切换焦点
          "Escape" — 取消/关闭
          "ArrowDown" — 下箭头
        """
        self.page.keyboard.press(key)

    # ═══════════════════════════════════════════════════════════
    #  五、复选框 / 下拉菜单
    # ═══════════════════════════════════════════════════════════

    def check(self, selector: str) -> None:
        """选中一个复选框或单选框。"""
        self.page.check(selector)

    def uncheck(self, selector: str) -> None:
        """取消选中一个复选框。"""
        self.page.uncheck(selector)

    def select_option(self, selector: str, value: str | list[str]) -> None:
        """
        从下拉菜单（<select> 标签）中选择一个选项。

        参数：
          selector: 下拉菜单的选择器
          value: 选项的 value 属性值，如 "beijing"
        """
        self.page.select_option(selector, value)

    def select_option_by_label(self, selector: str, label: str) -> None:
        """
        通过可见文字选择下拉菜单的选项。

        参数：
          selector: 下拉菜单的选择器
          label: 页面上看到的文字，如 "北京"（不是 value）
        """
        self.page.select_option(selector, label=label)

    # ═══════════════════════════════════════════════════════════
    #  六、获取页面信息
    # ═══════════════════════════════════════════════════════════

    def get_text(self, selector: str) -> str:
        """获取某个元素的文本内容。"""
        return self.page.inner_text(selector)

    def get_attribute(self, selector: str, attr: str) -> str | None:
        """
        获取某个元素的属性值。

        例如：get_attribute("#logo", "src") 获取 logo 图片的网址
        """
        return self.page.get_attribute(selector, attr)

    def get_value(self, selector: str) -> str:
        """获取输入框当前的值。"""
        return self.page.input_value(selector)

    # ═══════════════════════════════════════════════════════════
    #  七、可见性判断
    # ═══════════════════════════════════════════════════════════

    def is_visible(self, selector: str, timeout: int | None = None) -> bool:
        """
        检查某个元素在页面上是否可见。

        返回 True 或 False，不会因为元素不存在而报错。
        """
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout or 5000)
            return True
        except Exception:
            return False

    def is_hidden(self, selector: str, timeout: int | None = None) -> bool:
        """检查某个元素是否隐藏。"""
        try:
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout or 5000)
            return True
        except Exception:
            return False

    def is_enabled(self, selector: str) -> bool:
        """检查某个元素是否可用（没被禁用）。"""
        return self.page.is_enabled(selector)

    # ═══════════════════════════════════════════════════════════
    #  八、截图
    # ═══════════════════════════════════════════════════════════

    def take_screenshot(self, name: str = "screenshot", full_page: bool = True) -> Path:
        """
        对当前页面截图并保存到 screenshots/ 目录。

        参数：
          name: 截图文件名（不含路径）
          full_page: 是否截取整个页面（包括滚动条以下的部分）

        返回：
          截图文件的完整路径
        """
        # 延迟导入是为了避免循环引用
        from config.settings import settings
        path = settings.SCREENSHOTS_DIR / f"{name}.png"
        self.page.screenshot(path=path, full_page=full_page)
        return path

    # ═══════════════════════════════════════════════════════════
    #  九、页面滚动
    # ═══════════════════════════════════════════════════════════

    def scroll_into_view(self, selector: str) -> None:
        """滚动页面，让某个元素出现在视野中。"""
        self.page.locator(selector).scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        """滚动到页面顶部。"""
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        """滚动到页面底部。"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # ═══════════════════════════════════════════════════════════
    #  十、运行 JavaScript
    #  某些特殊场景需要直接执行 JS 代码
    # ═══════════════════════════════════════════════════════════

    def execute_script(self, script: str, *args) -> Any:
        """
        在浏览器中执行一段 JavaScript 代码。

        例如：execute_script("return navigator.userAgent")
        可以获取浏览器的 User-Agent 信息。
        """
        return self.page.evaluate(script, *args)

    # ═══════════════════════════════════════════════════════════
    #  十一、弹窗处理
    # ═══════════════════════════════════════════════════════════

    def accept_alert(self) -> None:
        """
        点击弹窗的"确认"按钮。

        用法：在触发弹窗的代码前调用：
          page.accept_alert()
          page.click("#delete-btn")  # 这会触发弹窗
        """
        self.page.once("dialog", lambda dialog: dialog.accept())

    def dismiss_alert(self) -> None:
        """
        点击弹窗的"取消"按钮。

        用法同上。
        """
        self.page.once("dialog", lambda dialog: dialog.dismiss())

    # ═══════════════════════════════════════════════════════════
    #  十二、Cookie 操作
    # ═══════════════════════════════════════════════════════════

    def set_cookie(self, name: str, value: str, url: str | None = None) -> None:
        """设置一个浏览器 Cookie。"""
        self.page.context.add_cookies([
            {"name": name, "value": value, "url": url or self.get_current_url()}
        ])

    def clear_cookies(self) -> None:
        """清除当前页面的所有 Cookie。"""
        self.page.context.clear_cookies()
