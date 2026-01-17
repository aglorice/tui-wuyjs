# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供项目上下文信息。

## 项目概述

**五邑大学研究生教务系统 TUI 终端版** - 一个基于 Python TUI 的教务系统查询工具，专为五邑大学研究生设计。

> 🎓 **本项目借助 AI 辅助开发完成**

**核心功能：**
- ✅ 自动登录（验证码 OCR 识别）
- ✅ 动态 RSA 公钥提取（每次登录从页面获取）
- ✅ 学生信息查询
- ✅ 课程表查询
- ✅ 成绩查询
- ✅ 考试安排查询
- ✅ 状态持久化
- ✅ AES/RSA 加密通信
- ✅ 现代 TUI 界面

## 开发环境

- **Python 版本**: 3.9+
- **虚拟环境**: `.venv/` (使用 virtualenv 创建)
- **IDE**: PyCharm 或 VS Code
- **主要依赖**: httpx, textual, pycryptodome, ddddocr, pydantic

## 快速开始

### 激活虚拟环境

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

### 运行测试

```bash
# 测试登录功能
python tests/test_login.py

# 测试 API 功能
python tests/test_api.py

# 测试考试查询
python tests/test_exam.py

# 测试学生信息
python tests/test_student_info.py
```

## 项目架构

```
yjsc/
├── src/
│   ├── core/                    # 核心模块
│   │   ├── constants.py         # 常量（RSA公钥、AES密钥）
│   │   ├── crypto.py            # AES/RSA 加密解密
│   │   └── config.py            # 配置管理
│   ├── client/                  # HTTP 客户端
│   │   ├── session.py           # Session ID 管理
│   │   └── http_client.py       # httpx 封装（自动解密）
│   ├── auth/                    # 认证模块
│   │   ├── captcha.py           # 验证码识别（ddddocr）
│   │   └── login.py             # 登录流程（动态提取公钥）
│   ├── api/                     # API 接口
│   │   ├── models.py            # Pydantic 数据模型
│   │   ├── course.py            # 课程表 API
│   │   ├── grade.py             # 成绩 API
│   │   ├── exam.py              # 考试 API
│   │   └── student.py           # 学生信息 API
│   ├── storage/                 # 状态持久化
│   │   └── state.py             # Session/凭据存储
│   └── ui/                      # TUI 界面
│       ├── app.py               # Textual 主应用
│       └── screens/             # UI 屏幕
│           ├── login.py         # 登录屏幕
│           └── dashboard.py     # 仪表盘（主界面）
├── tests/                       # 测试脚本
│   ├── test_login.py           # 登录测试
│   ├── test_api.py             # API 测试
│   ├── test_exam.py            # 考试测试
│   └── test_student_info.py    # 学生信息测试
├── main.py                      # 程序入口
├── requirements.txt             # 依赖列表
├── DOCUMENT.md                  # API 逆向文档
├── CLAUDE.md                    # 本文件
└── README.md                    # 用户文档
```

## 加密机制

### 1. 密码加密（RSA）

**重要：每次登录动态从服务器获取 RSA 公钥**

- 公钥存储在登录页面 HTML 的 `<input id="pubkey">` 元素中
- 使用 RSA with PKCS1_v1_5 padding 加密密码
- 备用硬编码公钥在 `src/core/constants.py`（用于降级）

**实现位置**：
- 动态提取：`src/auth/login.py:_get_rsa_pubkey_from_html()`
- 硬编码常量：`src/core/constants.py`

### 2. 响应加密（AES）

所有 API 响应都使用 AES-ECB 加密后 Base64 编码：

- **模式**: AES-ECB
- **填充**: PKCS7
- **密钥**: 从硬编码值派生（24字节）
- **实现**: `src/core/crypto.py`

### 3. Session 管理

ASP.NET Session IDs，格式：`/(S(session_id))/`

**实现**: `src/client/session.py`

## 登录流程

**关键：动态 RSA 公钥提取**

1. 初始化 Session → GET 首页 → 提取 Session ID
2. **获取登录页面 HTML** → 提取 RSA 公钥（正则表达式）
3. 下载验证码图片
4. OCR 识别验证码（ddddocr）
5. 使用提取的 RSA 公钥加密密码
6. POST 登录请求到 `/home/stulogin_do`
7. 自动重试（最多3次，验证码识别失败）

**代码位置**：`src/auth/login.py`

## 核心 API 端点

### 学生信息
```
GET /student/default/getxscardinfo?_=timestamp
```

### 课程表
```
POST /student/pygl/py_kbcx_ew
Data: kblx=xs&termcode=<学期代码>
```

### 成绩
```
GET /student/pygl/xscjcx_list?_=timestamp
```

### 考试
```
POST /student/pygl/kckccx_list
Data: {}
```

## 关键依赖

- **httpx**: 异步 HTTP 客户端
- **textual**: 现代 TUI 框架
- **pycryptodome**: AES/RSA 加密
- **ddddocr**: 验证码 OCR 识别
- **pydantic**: 数据验证模型
- **keyring**: 系统密码存储

## 开发指南

### 添加新的 API 端点

1. 在 `src/api/models.py` 添加 Pydantic 模型（如需要）
2. 在 `src/api/` 创建新文件或在现有文件添加方法
3. 使用 `self.client.get()` 或 `self.client.post()` - 响应自动解密
4. 在仪表盘 (`src/ui/screens/dashboard.py`) 添加 UI 显示

**示例**：

```python
# src/api/your_api.py
class YourAPI:
    def __init__(self, client: YJSClient):
        self.client = client

    async def get_data(self) -> list[YourModel]:
        if not self.client.is_logged_in:
            raise Exception("未登录")

        response = await self.client.get('/api/endpoint')
        # 响应已自动解密
        return [YourModel(**item) for item in response]
```

### 修改加密逻辑

⚠️ **警告**: 修改加密可能导致与服务器不兼容

**相关文件**：
- `src/core/constants.py` - 密钥定义
- `src/core/crypto.py` - 加解密实现
- `src/auth/login.py` - RSA 公钥提取逻辑

### UI 修改

**主应用**: `src/ui/app.py`
**登录屏幕**: `src/ui/screens/login.py`
**仪表盘**: `src/ui/screens/dashboard.py`

Textual TUI 框架：
- 使用 `ComposeResult` 定义界面结构
- CSS 在类的 `CSS` 属性中定义
- 事件处理：`on_button_pressed()`, `on_mount()` 等

## 重要文件

- `DOCUMENT.md` - 完整的 API 逆向工程文档
- `src/core/crypto.py` - 所有加密逻辑
- `src/client/http_client.py` - 自动解密中间件
- `src/auth/login.py` - 登录流程（动态公钥提取）
- `src/ui/screens/dashboard.py` - 主界面
- `tests/` - 功能测试脚本

## 测试说明

### 测试脚本

所有测试脚本都使用 `input()` 和 `getpass()` 安全获取凭证，不会硬编码账号密码。

运行测试时需要交互式输入学号和密码。

### 调试技巧

1. **启用详细日志**：在代码中添加 `print()` 语句
2. **测试单个功能**：使用 `tests/` 下的测试脚本
3. **验证登录**：先运行 `test_login.py` 验证登录功能
4. **检查网络**：确保能访问 `yjsc.wyu.edu.cn`

## 常见问题

### Q: 登录后提示"未登录"？
A: 检查 Cookie/Session 是否正确保存，尝试重新登录

### Q: 验证码识别失败？
A: 程序会自动重试 3 次，如仍失败，请手动重试

### Q: 响应解密失败？
A: 可能是密钥不匹配或服务器更新了加密方式，检查 `src/core/crypto.py`

### Q: 界面显示异常？
A: 确保终端支持 TUI，尝试调整终端窗口大小

## AI 辅助开发

本项目在 AI 辅助下完成，主要使用了：
- Claude Code 用于代码生成和重构
- AI 辅助 API 逆向分析
- AI 辅助 TUI 界面设计

开发时请注意：
- 保持代码风格一致
- 添加必要的注释
- 编写清晰的文档
- 使用 Pydantic 进行数据验证

## 安全注意事项

1. ✅ **不要硬编码账号密码** - 使用 `input()` 和 `getpass()`
2. ✅ **不要提交敏感信息** - 检查 `.gitignore`
3. ✅ **使用系统 keyring** - 安全存储用户凭据
4. ✅ **保护加密密钥** - 虽然 `constants.py` 有硬编码，但这是逆向结果
5. ⚠️ **仅用于学习** - 遵守学校规定，合理使用

## 代码风格

- 使用类型提示（Type Hints）
- Pydantic 模型用于数据验证
- 异步函数（async/await）
- 清晰的注释和文档字符串
- 遵循 PEP 8 规范

## 许可证

MIT License - 仅供学习交流使用