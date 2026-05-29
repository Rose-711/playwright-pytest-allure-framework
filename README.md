# 🧪 自动化测试框架

> Python + Playwright + Pytest + Allure

[![CI](https://github.com/Rose-711/automation-test-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/Rose-711/automation-test-framework/actions/workflows/ci.yml)

一个**面向初学者的**、**开箱即用的** Web UI 自动化测试框架。  
帮你自动打开浏览器、操作页面、检查结果，最后生成漂亮的测试报告。

---

## 📖 这是干什么的？

假设你要测试百度搜索好不好用，传统做法是：

```
1. 打开 Chrome
2. 输入 www.baidu.com
3. 在搜索框输入 "Python"
4. 点击搜索按钮
5. 看有没有搜索结果
```

有了这个框架，你只需要写几行代码，以后每次测试都是**自动的**：

```python
def test_baidu_search(page):
    baidu = BaiduPage(page)   # 调出百度页面
    baidu.open()              # 打开百度
    baidu.search("Python")    # 搜索
    assert baidu.result_items.count() > 0  # 检查结果
```

> ⏱ 跑一次只需要几秒钟，而且你可以同时测几十个不同的功能。

---

## 🚀 快速开始（5分钟上手）

### 环境要求

- Python 3.10 或更高版本
- Windows / macOS / Linux
- Chrome 浏览器（已安装）

### 安装

打开终端（命令行），依次执行：

```bash
# 1. 进入项目目录
cd D:/VibeCoding/automation-test-framework

# 2. 安装依赖（只跑一次）
pip install -r requirements.txt
```

### 运行测试

```bash
# 跑所有测试
pytest

# 只跑冒烟测试（最快的那些）
pytest -m smoke

# 只看百度搜索的测试
pytest tests/test_baidu.py -v
```

看到一片绿色的 `PASSED` ✅ 就说明成功了！

---

## 📂 项目结构（每个文件是干啥的）

```
automation-test-framework/
│
├── conftest.py              ← 【总控】全局配置，管理浏览器启动/关闭
├── pytest.ini               ← 【设置】Pytest 的配置文件
├── requirements.txt         ← 【依赖】需要安装的 Python 库
├── .env.example             ← 【模板】配置项模板（复制为 .env 使用）
│
├── config/
│   ├── __init__.py
│   └── settings.py          ← 【配置】读取 .env 文件，提供全局设置
│
├── pages/
│   ├── __init__.py          ← 【核心】BasePage 基类（所有页面操作的"工具箱"）
│   ├── baidu_page.py        ← 百度页面的操作方法
│   └── example_page.py      ← example.com 页面的操作方法
│
├── tests/
│   ├── conftest.py          ← 测试专用的 fixtures
│   ├── test_baidu.py        ← 【百度搜索测试】搜索、导航
│   ├── test_interactions.py ← 【UI交互测试】复选框、下拉菜单、表单、动态内容
│   ├── test_api.py          ← 【API测试】GET/POST/PUT/DELETE 接口
│   ├── test_example.py      ← 示例测试（入门参考）
│   └── test_search.py       ← 另一个示例
│
├── utils/
│   ├── helpers.py           ← 【工具】随机数据生成、重试机制
│   ├── data_loader.py       ← 【数据】从 JSON/YAML 读取测试数据
│   └── reporter.py          ← 【报告】Allure 报告辅助函数
│
├── testdata/
│   ├── test_data.json       ← 测试数据文件
│   └── test_page.html       ← 本地测试页面（无需网络）
│
├── screenshots/             ← 测试失败时的截图自动保存到这里
└── reports/                 ← Allure 测试报告输出目录
```

---

## 🧠 核心概念（大白话版）

### 1️⃣ Page Object（页面对象）

把网页"封装"成一个 Python 类。

```
❌ 不封装：每个测试都写 page.fill("#kw", "xxx") 和 page.click("#su")
✅ 封装后：BaiduPage(page).search("xxx")   ← 一句话搞定
```

**好处：** 如果百度改了搜索框的 ID，只需要改 `BaiduPage` 一个地方，所有测试自动生效。

### 2️⃣ Fixture（测试准备）

Pytest 的一种机制——自动准备测试需要的东西。

比如每个测试前都要打开浏览器，写成 fixture 后：

```python
# 测试只需要写这个：
def test_something(page):   # ← page 参数自动注入
    page.goto("https://...")
```

你不用自己 new_page()，也不用 close()，Pytest 全包了。

### 3️⃣ 参数化

一个测试函数测多组数据：

```python
@pytest.mark.parametrize("keyword", ["Playwright", "Python", "自动化测试"])
def test_search(self, page, keyword):
    # 这个测试会跑 3 次，分别用 3 个关键字
```

### 4️⃣ 标签

给测试打标签，想跑哪些就跑哪些：

```python
@pytest.mark.smoke       # 冒烟测试（核心功能快速检查）
@pytest.mark.regression  # 回归测试（全面覆盖）
```

```bash
pytest -m smoke       # 只跑冒烟
pytest -m regression  # 只跑回归
pytest -m "not slow"  # 跳过慢速测试
```

### 5️⃣ Allure 报告

测试跑完后，生成一个漂亮的 HTML 网页报告，包含：

- 测试通过/失败统计
- 每个测试的执行步骤
- 失败时的截图
- 测试分类（按 feature/story 分组）

---

## 💻 常用命令大全

```bash
# ── 运行测试 ──

pytest                          # 跑全部测试
pytest -v                       # 显示详细结果
pytest -m smoke                 # 只跑冒烟测试
pytest -m regression            # 只跑回归测试
pytest tests/test_baidu.py      # 只跑百度测试
pytest -k "baidu"               # 跑名字包含 "baidu" 的测试
pytest -k "api"                 # 跑名字包含 "api" 的测试

# ── 调试相关 ──

pytest --headed                 # 显示浏览器窗口（默认后台运行）
pytest -s                       # 显示 print() 输出
pytest --tb=long                # 显示完整报错信息（默认 short）
pytest --reruns 2               # 失败后重试 2 次

# ── 性能相关 ──

pytest -n 4                     # 4 个测试并行跑（更快）
pytest -x                       # 遇到第一个失败就停止（省时间）
pytest --run-slow               # 包含慢速测试

# ── 报告相关 ──

pytest --alluredir=reports/allure-results   # 生成 Allure 数据
allure serve reports/allure-results         # 打开 Allure 报告

# ── 切换浏览器 ──

pytest --browser firefox        # 用 Firefox 跑（需要安装）
pytest --browser webkit         # 用 WebKit（Safari）跑

# ── 指定网址 ──

pytest --base-url https://example.com  # 指定被测网址
```

---

## 📝 一步步教你写新测试

假设你要测试**登录功能**，按以下步骤来：

### 第 1 步：创建页面对象

在 `pages/` 下新建 `login_page.py`：

```python
from pages import BasePage

class LoginPage(BasePage):
    """登录页面对象。"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://example.com/login"

    def login(self, username, password):
        """封装登录操作。"""
        self.navigate(self.url)           # 打开登录页
        self.fill("#username", username)  # 输入用户名
        self.fill("#password", password)  # 输入密码
        self.click("#login-btn")          # 点登录按钮

    def get_error_message(self):
        """获取登录失败的错误提示。"""
        return self.get_text(".error-msg")

    def is_logged_in(self):
        """检查是否登录成功（看有没有退出按钮）。"""
        return self.is_visible(".logout-btn")
```

### 第 2 步：写测试用例

在 `tests/` 下新建 `test_login.py`：

```python
import allure
import pytest
from pages.login_page import LoginPage

@allure.feature("登录模块")
class TestLogin:

    @allure.title("使用正确的账号密码应登录成功")
    @pytest.mark.smoke
    def test_valid_login(self, page):
        login_page = LoginPage(page)
        login_page.login("admin", "123456")
        assert login_page.is_logged_in(), "登录成功后应看到退出按钮"

    @allure.title("使用错误的密码应提示错误")
    @pytest.mark.regression
    def test_invalid_login(self, page):
        login_page = LoginPage(page)
        login_page.login("admin", "wrong_password")
        error = login_page.get_error_message()
        assert "密码错误" in error, f"应提示密码错误，实际提示：{error}"
```

### 第 3 步：运行验证

```bash
pytest tests/test_login.py -v --headed
```

浏览器会自动弹出来，你就能看到它在自动操作了！

---

## 🔧 配置说明

复制 `.env.example` 为 `.env`，然后修改里面的值：

```ini
# 浏览器类型：chromium | firefox | webkit
BROWSER=chromium

# 无头模式：true = 不显示浏览器窗口（CI 用）
HEADLESS=false

# 操作延迟（毫秒），设大一点看起来更像真人
SLOW_MO=0

# 浏览器窗口大小
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720

# 被测网址
BASE_URL=https://example.com

# 超时时间（毫秒）
DEFAULT_TIMEOUT=30000

# 失败重试次数
RETRY_TIMES=0
```

---

## 🧪 当前测试统计

| 套件 | 文件 | 数量 | 类型 |
|------|------|------|------|
| 百度搜索 | `test_baidu.py` | 8 个 | 冒烟+回归 |
| UI 交互 | `test_interactions.py` | 15 个 | 冒烟+回归 |
| API 接口 | `test_api.py` | 8 个 | 冒烟+回归 |
| 示例测试 | `test_example.py` | 7 个 | 冒烟+回归 |
| 示例搜索 | `test_search.py` | 3 个 | 冒烟 |
| **合计** | | **41 个** | ✅ 全部通过 |

---

## ❓ 常见问题

### Q：测试跑得太慢怎么办？

```bash
pytest -n 4              # 4 个测试并行跑
pytest -m smoke          # 只跑最重要的
pytest -x                # 挂了一个就停
```

### Q：测试失败了我怎么看？

1. 先看控制台输出的错误信息
2. 去 `reports/allure-results/` 下看完整报告
3. 去 `screenshots/` 看失败时的截图

```bash
allure serve reports/allure-results   # 用浏览器打开报告
```

### Q：不想让浏览器弹出来？

`pytest` 默认就是无头模式（不弹窗口）。  
如果想看浏览器操作，加 `--headed`。

### Q：如何更新 Playwright 的浏览器？

```bash
playwright install chromium    # 安装 Chromium
playwright install --force     # 强制重装
```

### Q：提示"找不到 Chrome"？

这个框架默认使用你系统安装的 Chrome。  
如果你没装 Chrome，或者想用 Playwright 自带的浏览器，可以修改 `conftest.py` 中的 `channel="chrome"` 配置。

---

## 🏗 框架设计原则

1. **简单优先** —— 让初学者能看懂、能用起来
2. **约定大于配置** —— 按框架的约定写，不用额外配置
3. **实用为主** —— 每个功能都是实际测试中会用到的
4. **中文友好** —— 注释、文档都用中文

---

## 📄 许可证

MIT License — 随便用，随便改。
