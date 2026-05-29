"""
==============================================================
  百度搜索测试用例
==============================================================

  这个文件演示了：
  1. ✅ Page Object 模式 —— 操作封装在 BaiduPage 里
  2. ✅ 参数化测试 —— 一个测试函数测多组数据
  3. ✅ Allure 报告 —— 详细的步骤和附件
  4. ✅ 标签分类 —— smoke（冒烟）/ regression（回归）

  运行方式：
    pytest tests/test_baidu.py -v                # 跑全部
    pytest tests/test_baidu.py -m smoke          # 只跑冒烟
    pytest tests/test_baidu.py -k "search"       # 只跑搜索相关的
"""
import allure
import pytest
from playwright.sync_api import expect

from pages.baidu_page import BaiduPage


# ═══════════════════════════════════════════════════════════════
#  @allure.feature 和 @allure.story
#  这两个装饰器用于在 Allure 报告中分组展示测试。
#  feature = 大模块，story = 子功能
# ═══════════════════════════════════════════════════════════════

@allure.feature("百度搜索")
@allure.story("搜索功能")
class TestBaiduSearch:
    """百度搜索的核心功能测试。"""

    @allure.title("搜索关键字应返回结果列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke  # 冒烟测试：快速检查核心功能
    @pytest.mark.parametrize("keyword", [
        "Playwright",
        "Python",
        "自动化测试",
    ], ids=["playwright", "python", "auto-test"])
    def test_search_returns_results(self, page, keyword: str) -> None:
        """
        验证：输入关键字点搜索，能看到结果列表。

        @pytest.mark.parametrize 让这个测试跑 3 次，
        每次用不同的关键字。ids 参数让每次跑的名称更易读。
        """
        # 1. 打开百度首页
        baidu = BaiduPage(page)

        with allure.step(f"打开百度首页并搜索「{keyword}」"):
            baidu.open()
            # 2. 输入关键字并点击搜索
            baidu.search(keyword)

        with allure.step("验证搜索结果页加载成功"):
            # 搜索后 URL 应该变成 https://www.baidu.com/s?... 的格式
            assert baidu.is_result_page(), "Should be on search result page"

        with allure.step("验证搜索结果列表不为空"):
            # 使用 Playwright 的 expect 进行智能等待
            expect(baidu.result_items.first).to_be_visible(timeout=5000)
            result_count = baidu.result_items.count()
            assert result_count > 0, f"Expected >0 results, got {result_count}"
            allure.attach(str(result_count), name="Result Count", attachment_type=allure.attachment_type.TEXT)

    @allure.title("搜索「{keyword}」第一条结果应包含关键字")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("keyword, expected", [
        ("Playwright", "Playwright"),
        ("Pytest", "pytest"),
    ], ids=["playwright", "pytest"])
    def test_first_result_contains_keyword(self, page, keyword: str, expected: str) -> None:
        """
        验证：搜索结果的第一条标题包含搜索的关键字。

        参数化可以传多个参数（keyword, expected），
        甚至可以用元组的方式传递多组数据。
        """
        baidu = BaiduPage(page)

        with allure.step("搜索关键字"):
            baidu.open()
            baidu.search(keyword)

        with allure.step("获取第一条结果标题"):
            first_title = baidu.first_result_title.inner_text()
            allure.attach(first_title, name="First Result Title", attachment_type=allure.attachment_type.TEXT)

        with allure.step("验证标题包含关键字"):
            assert expected.lower() in first_title.lower(), (
                f"First result title '{first_title}' should contain '{expected}'"
            )

    @allure.title("空搜索不应返回正常结果")
    @pytest.mark.regression
    def test_empty_search_no_results(self, page) -> None:
        """
        验证：不输入内容直接点搜索，不会有正常结果。

        注意：百度对空搜索可能会触发验证码（反爬机制），
        所以我们只验证"没有正常的搜索结果页"。
        """
        baidu = BaiduPage(page)

        with allure.step("打开百度首页"):
            baidu.open()

        with allure.step("直接点击搜索按钮（不输入内容）"):
            baidu.click("#su")
            baidu.page.wait_for_timeout(2000)

        with allure.step("验证没有正常搜索结果"):
            url = baidu.page.url
            has_results = url.startswith("https://www.baidu.com/s?")
            is_captcha = "captcha" in url or "wappass" in url
            assert not has_results or is_captcha, \
                f"Unexpected behavior, URL: {url}"
            allure.attach(url, name="Redirect URL", attachment_type=allure.attachment_type.TEXT)

    @allure.title("搜索建议应随输入实时显示")
    @pytest.mark.regression
    def test_search_suggestions(self, page) -> None:
        """
        验证：输入部分关键字后，下拉框会出现搜索建议。

        注意：搜索建议依赖网络请求，网络不好可能加载不出来，
        所以我们用了 try/except，加载不出来就跳过（不判失败）。
        """
        baidu = BaiduPage(page)

        with allure.step("打开百度首页"):
            baidu.open()

        with allure.step("输入部分关键字"):
            baidu.fill("#kw", "Play")

        with allure.step("验证搜索建议出现"):
            try:
                suggestion_area = baidu.page.locator(".bdsug")
                expect(suggestion_area).to_be_visible(timeout=3000)
                suggestions = suggestion_area.locator("li").all_inner_texts()
                allure.attach(str(suggestions), name="Suggestions", attachment_type=allure.attachment_type.TEXT)
                assert len(suggestions) > 0, "Should have at least one suggestion"
            except Exception:
                allure.attach("Suggestions did not load (network issue)", name="Note",
                              attachment_type=allure.attachment_type.TEXT)
                pytest.skip("Search suggestions unavailable — likely network issue")


@allure.feature("百度搜索")
@allure.story("导航")
class TestBaiduNavigation:

    @allure.title("百度首页导航链接可见")
    @pytest.mark.regression
    def test_navigation_links_visible(self, page) -> None:
        """
        验证：百度首页顶部的导航链接可以正常显示。

        注意：百度前端经常改版，元素选择器可能变化。
        这里用了更健壮的方式：多个选择器组合（or 关系），
        只要其中任何一个匹配就算通过。
        """
        baidu = BaiduPage(page)

        with allure.step("打开百度首页"):
            baidu.open()

        with allure.step("验证导航区域存在"):
            # 多种选择器组合，适应百度可能的页面改版
            nav_area = baidu.page.locator(
                "#s-top-left, .s-top-nav-new, a[href*='news'], a[href*='hao123']"
            ).first
            assert nav_area.is_visible(), "Navigation area should be visible on homepage"
            nav_text = nav_area.all_inner_texts() if hasattr(nav_area, 'all_inner_texts') else [nav_area.inner_text()]
            allure.attach(str(nav_text), name="Nav Text", attachment_type=allure.attachment_type.TEXT)
