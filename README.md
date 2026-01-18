# 五邑大学研究生教务系统 - TUI终端版

> 🎓 **本项目借助 AI 辅助开发完成** - 为五邑大学研究生提供高效便捷的终端版教务查询工具

基于 TUI（Terminal User Interface）的教务系统查询工具，提供现代化的命令行交互方式，让查询更高效！

## ✨ 功能特性

- ✅ **自动登录** - 验证码自动识别（ddddocr）
- ✅ **动态RSA公钥** - 每次登录从页面提取最新公钥
- ✅ **学生信息** - 查看个人基本信息
- ✅ **课程表查询** - 完整的每周课程安排
- ✅ **成绩查询** - 历史成绩与学分统计
- ✅ **考试安排** - 考试时间、地点、座位信息
- ✅ **状态持久化** - 记住登录状态
- ✅ **安全存储** - 账号密码安全保存（可选）
- ✅ **现代界面** - 美观的 TUI 界面设计

## 📸 界面预览

```
┌─────────────────────────────────────────┐
│     🎓 YJS 教务系统                      │
├─────────────────────────────────────────┤
│  👤 学生信息                             │
│  学号: 2211111111    姓名: 张三          │
│  学院: 计算机学院    专业: 软件工程      │
├──────────┬────────────────────────────┤
│  📚 成绩 │  📊 数据列表                 │
│  📅 课程表│                               │
│  ✏️ 考试  │  [表格显示区域]              │
│          │                               │
├──────────┴────────────────────────────┤
│         [🔄 刷新]  [🚪 退出]           │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 终端支持 TUI（推荐现代终端如 iTerm2、Windows Terminal）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd yjsc
```

#### 2. 创建虚拟环境

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 💻 使用方法

### 启动应用

```bash
python main.py
```

首次启动会显示登录界面，输入你的学号和密码即可登录。

### 界面操作

| 按键 | 功能 |
|------|------|
| `Tab` | 切换焦点 |
| `Enter` | 确认/提交 |
| `↑↓←→` | 在表格中移动 |
| `Esc` | 返回上一级 |
| `Ctrl+C` | 退出应用 |

### 测试功能

如果只想测试某个功能是否正常工作：

```bash
# 测试登录
python tests/test_login.py

# 测试课程表和成绩
python tests/test_api.py

# 测试考试查询
python tests/test_exam.py

# 测试学生信息
python tests/test_student_info.py
```

## 🏗️ 项目结构

```
yjsc/
├── src/
│   ├── core/                # 核心模块
│   │   ├── constants.py     # 常量（RSA公钥、AES密钥）
│   │   ├── crypto.py        # 加密解密实现
│   │   └── config.py        # 配置管理
│   ├── client/              # HTTP 客户端
│   │   ├── session.py       # Session ID 管理
│   │   └── http_client.py   # HTTP 封装（自动解密）
│   ├── auth/                # 认证模块
│   │   ├── captcha.py       # 验证码识别
│   │   └── login.py         # 登录流程
│   ├── api/                 # API 接口
│   │   ├── models.py        # 数据模型
│   │   ├── course.py        # 课程表 API
│   │   ├── grade.py         # 成绩 API
│   │   ├── exam.py          # 考试 API
│   │   └── student.py       # 学生信息 API
│   ├── storage/             # 状态存储
│   │   └── state.py         # 凭据持久化
│   └── ui/                  # TUI 界面
│       ├── app.py           # 主应用
│       └── screens/         # 界面
│           ├── login.py     # 登录界面
│           └── dashboard.py # 主仪表盘
├── tests/                   # 测试脚本
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
├── DOCUMENT.md              # API 逆向文档
├── CLAUDE.md                # 开发指南
└── README.md                # 本文件
```

## 🔧 技术栈

- **HTTP 客户端**: httpx - 异步 HTTP 请求
- **TUI 框架**: textual - 现代终端界面
- **加密**: pycryptodome - AES/RSA 加密
- **验证码识别**: ddddocr - OCR 验证码识别
- **数据验证**: pydantic - 数据模型验证
- **密码存储**: keyring - 系统安全存储

## 🔐 安全特性

1. **RSA 公钥动态提取** - 每次登录从服务器获取最新公钥
2. **AES 响应解密** - 自动解密服务器加密的响应
3. **安全密码存储** - 使用系统 keyring 存储密码（可选）
4. **Session 管理** - 自动管理登录状态

## 📖 登录流程

```
1. 访问首页 → 获取 Session ID
2. 访问登录页 → 提取 RSA 公钥（动态）
3. 下载验证码 → OCR 识别
4. RSA 加密密码 → 使用动态公钥
5. POST 登录请求 → 携带加密密码和验证码
6. 自动重试 → 验证码识别失败最多重试 3 次
```

## ❓ 常见问题

### Q: 登录失败怎么办？

A: 请检查以下几点：
- 学号和密码是否正确
- 网络连接是否正常
- 多试几次（验证码识别可能需要重试）
- 查看错误信息提示

### Q: 界面显示不正常？

A:
- 确保终端支持 TUI
- 尝试调整终端窗口大小
- 使用测试脚本验证功能：`python tests/test_login.py`

### Q: 如何保存账号密码？

A: 勾选登录界面的"记住密码"选项，密码会安全存储在系统 keyring 中。

### Q: 验证码识别准确率如何？

A: ddddocr 对简单验证码识别率较高，但可能需要重试。程序会自动重试最多 3 次。

## 📚 详细文档

- **[DOCUMENT.md](DOCUMENT.md)** - 完整的 API 逆向工程文档
- **[CLAUDE.md](CLAUDE.md)** - 面向开发者的架构指南

## 🙏 开发说明

本项目借助 AI 辅助开发完成，主要用于学习和个人使用。如果有任何问题或建议，欢迎提出！

## ⚠️ 注意事项

1. **仅供学习交流使用** - 请勿用于商业用途
2. **遵守学校规定** - 合理使用教务系统接口
3. **密码安全** - 不要在公共环境中保存密码
4. **网络环境** - 建议在稳定网络环境下使用

## 📄 许可证

MIT License

---

**Made with ❤️ for WYU Graduate Students**