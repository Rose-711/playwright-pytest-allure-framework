# Automation Test Framework

基于 **Python + Playwright + Pytest + Allure** 的自动化测试框架。

## 技术栈

| 组件     | 用途                        |
| -------- | --------------------------- |
| Python   | 编程语言 (>=3.10)           |
| Playwright | 浏览器自动化                |
| Pytest   | 测试运行框架                |
| Allure   | 测试报告                    |
| pytest-xdist | 并行执行               |
| pytest-rerunfailures | 失败重试         |

## 项目结构

```
automation-test-framework/
├── config/          # 配置模块
│   ├── __init__.py
│   └── settings.py  # 环境变量 & 配置
├── pages/           # Page Object 模式
│   ├── __init__.py  # BasePage 基类
│   └── example_page.py
├── tests/           # 测试用例
│   ├── conftest.py  # 测试级 fixtures
│   ├── test_example.py
│   └── test_search.py
├── utils/           # 工具函数
│   ├── helpers.py
│   ├── data_loader.py
│   └── reporter.py
├── testdata/        # 测试数据 (JSON/YAML)
├── screenshots/     # 失败截图
├── reports/         # 测试报告
├── conftest.py      # 全局 fixtures (Playwright)
├── pytest.ini       # Pytest 配置
├── pyproject.toml   # 项目依赖
└── .env.example     # 环境变量模板
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置 BASE_URL 等参数
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 仅运行冒烟测试
pytest -m smoke

# 运行回归测试
pytest -m regression

# 带 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results

# 并行执行 (4 进程)
pytest -n 4

# 失败重试 (最多 2 次)
pytest --reruns 2

# 使用 Firefox
pytest --browser firefox

# 有头模式 (看到浏览器界面)
pytest --headed
```

### 4. 查看 Allure 报告

```bash
# 需要先安装 Allure 命令行工具
# https://docs.qameta.io/allure-report/#_installing_a_commandline

allure serve reports/allure-results
```

## 编写测试

### Page Object 模式

```python
# pages/login_page.py
from pages import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{settings.BASE_URL}/login"

    @property
    def username_input(self):
        return self.page.locator("#username")

    @property
    def password_input(self):
        return self.page.locator("#password")

    @property
    def login_button(self):
        return self.page.locator("button[type='submit']")

    def login(self, username: str, password: str) -> None:
        self.navigate(self.url)
        self.fill("#username", username)
        self.fill("#password", password)
        self.click("button[type='submit']")
```

### 测试用例

```python
import allure
import pytest

@allure.feature("登录模块")
class TestLogin:
    @allure.title("使用有效凭据登录")
    @pytest.mark.smoke
    def test_valid_login(self, login_page):
        login_page.login("admin", "admin123")
        assert login_page.is_visible(".dashboard")
```

## 标签说明

| 标签        | 用途               |
| ----------- | ------------------ |
| `smoke`     | 冒烟测试 (快速)    |
| `regression`| 回归测试           |
| `critical`  | 关键路径测试       |
| `slow`      | 慢速测试 (默认跳过) |

运行 `pytest --run-slow` 可包含慢速测试。
