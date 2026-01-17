# 五邑大学研究生教务系统 - API 技术文档

> 🎓 **本项目借助 AI 辅助开发完成**

## 项目概述

本文档记录了五邑大学研究生教务系统（https://yjsc.wyu.edu.cn）的 API 逆向工程分析结果，用于构建 TUI 终端版查询工具。

## 基础信息

- **系统地址**: https://yjsc.wyu.edu.cn
- **Session 格式**: ASP.NET Session - `/(S(session_id))/`
- **主要通信方式**: AJAX + 加密响应
- **开发语言**: Python 3.9+

---

## 1. 加密机制

### 1.1 密码加密（RSA）

**公钥获取方式**：
- **主要方式**: 动态从登录页面 HTML 提取
- **备用方式**: 使用硬编码公钥（降级方案）

**公钥存储位置**：
```html
<input id="pubkey" type="hidden" value="-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUdfasa4GNADCBiQKBgQCl7wsnDasd1wAKpSPjfWAvE7m7
3cfIdcbJyxN0tDfx74a/olTOMFJMc6NryGdaOMZvMfRZq1sasdu7Ux/y6Un6WWnm
AdZ0x+Zm+s2NHzjds99YszN+LHakQyyE/2EU8svTiLXgH3SkC89O2ulGgz2uCzKf
qnBgeKrCuKPVufB3cwIDAQAB
-----END PUBLIC KEY-----">
```

**加密流程**：
```javascript
var rsa = new JSEncrypt();
rsa.setPublicKey($("#pubkey").val());  // 从 HTML 获取
var rsa_p = rsa.encrypt(password);      // RSA 加密
```

**Python 实现**：
```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

def encrypt_password(password: str, pubkey_pem: str) -> str:
    """RSA PKCS1_v1_5 加密密码"""
    key = RSA.import_key(pubkey_pem)
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(password.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')
```

**动态提取实现** (`src/auth/login.py`):
```python
import re

async def _get_rsa_pubkey_from_html(self) -> str:
    login_url = self.client.session.build_url('/home/stulogin')
    response = await self.client.session.client.get(login_url)
    html = response.text

    # 正则提取公钥
    pattern = r'<input\s+id="pubkey"[^>]*value="([^"]*)"'
    match = re.search(pattern, html)

    if match:
        pubkey = match.group(1)
        # HTML 实体解码
        pubkey = pubkey.replace('&lt;', '<').replace('&gt;', '>')
        return pubkey

    raise Exception("无法从登录页面获取 RSA 公钥")
```

### 1.2 响应加密（AES-ECB）

**密钥派生**：
```javascript
// 硬编码的加密密钥（Base64）
var desKey1 = 'ND7TLBY9Cx/SdS0R/7dqmg==';
var desKey3 = 'ZXF3+Q3opQHlh6UkTTFRVA==';
var desKey5 = '==QrlklM2cjROKp18sqnxLd2'.reverse();

// 解密密钥
var decryptKey = 'sopthsk!#032IJDS'.reverse();  // 'SDJI230#!kshthpos'

// 最终 AES 密钥
var aesKey = Decrypt2(desKey1, decryptKey) +
             Decrypt2(desKey3, decryptKey) +
             Decrypt2(desKey5, decryptKey);
```

**AES 参数**：
- **算法**: AES
- **模式**: ECB
- **填充**: PKCS7
- **密钥长度**: 192 位（24 字节）

**自动解密拦截器**：
```javascript
// jQuery Ajax 拦截器
(function($) {
    var _ajax = $.ajax;
    $.ajax = function(options) {
        var success = options.success;
        options.success = function(data, status, xhr) {
            let decrypted = '';
            try {
                decrypted = Decrypt2(data, aesKey);  // 自动 AES 解密
            } catch (e) {
                decrypted = 'error';
            }
            let parsed = JSON.parse(decrypted);
            return success(parsed, status, xhr);
        };
        return _ajax(options);
    };
})(jQuery);
```

**Python 解密实现** (`src/core/crypto.py`):
```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

def aes_decrypt(ciphertext: str, key: bytes) -> str:
    """AES-ECB-PKCS7 解密"""
    if ciphertext == "==gwJPTxzG0iY2qTiSUo7wB6"[::-1]:
        return '-'

    encrypted = base64.b64decode(ciphertext)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted.decode('utf-8')
```

---

## 2. Session 管理

### 2.1 Session ID 格式

```
https://yjsc.wyu.edu.cn/(S(session_id))/path/to/resource
                      └──────────┘
                   ASP.NET Session ID
```

### 2.2 获取流程

```python
import re
import httpx

async def get_session_id() -> str:
    """获取 ASP.NET Session ID"""
    async with httpx.AsyncClient() as client:
        # 1. 访问首页
        response = await client.get(
            'https://yjsc.wyu.edu.cn/',
            follow_redirects=True
        )

        # 2. 从重定向后的 URL 提取 Session ID
        # URL 格式: https://yjsc.wyu.edu.cn/(S(abc123))/home/stulogin
        match = re.search(r'\(S\(([^)]+)\)\)', str(response.url))
        if match:
            return match.group(1)

        raise Exception('无法获取 Session ID')
```

---

## 3. 登录流程

### 3.1 完整流程

```
┌─────────────────┐
│  访问首页        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 获取 Session ID │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 获取登录页面 HTML│
│ 提取 RSA 公钥    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 下载验证码图片  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OCR 识别验证码  │
│ (ddddocr)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RSA 加密密码    │
│ (使用动态公钥)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ POST 登录请求  │
│ /home/stulogin_do
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 自动重试（最多3次）│
└─────────────────┘
```

### 3.2 登录接口

**请求**：
```
POST https://yjsc.wyu.edu.cn/(S(session_id))/home/stulogin_do

Content-Type: application/x-www-form-urlencoded

json={"UserId":"学号","Password":"<RSA加密的密码>","VeriCode":"验证码","url":"","city":""}
```

**响应**（AES 加密）：
```json
{
    "jg": "1",
    "msg": "登录成功",
    "url": "target_page"
}
```

### 3.3 验证码

**获取验证码**：
```
GET https://yjsc.wyu.edu.cn/(S(session_id))/Home/VerificationCode?codetype=stucode&t=<timestamp>
```

**识别方案**（ddddocr）：
```python
import ddddocr

async def recognize_captcha(image_bytes: bytes) -> str:
    """使用 ddddocr 识别验证码"""
    ocr = ddddocr.DdddOcr()
    return ocr.classification(image_bytes)
```

---

## 4. 核心 API 端点

### 4.1 学生信息

**请求**：
```
GET /student/default/getxscardinfo?_=<timestamp>
```

**响应**（AES 加密）：
```json
[{
    "xh": "2211111111",          // 学号
    "xm": "张三",                // 姓名
    "xsmc": "计算机学院",         // 学院名称
    "zymc": "软件工程",           // 专业名称
    "xslb": "全日制专业学位硕士", // 学生类别
    "dsxm": "导师姓名",           // 导师
    "dsxm1": "",                 // 导师1
    "dsxm2": "",                 // 导师2
    "dsxm3": "",                 // 导师3
    "nj": "2025",                // 年级
    "dsinfo": "导师姓名"          // 导师信息
}]
```

### 4.2 课程表

**请求**：
```
POST /student/pygl/py_kbcx_ew

Content-Type: application/x-www-form-urlencoded

kblx=xs&termcode=<学期代码>
```

**响应**（AES 加密）：
```json
{
    "rows": [{
        "jcid": 1,
        "sjbz": "上午",
        "mc": "1",
        "kch": "课程编号",
        "kcmc": "课程名称",
        "jsxx": "教师",
        "jsxm": "教师姓名",
        "jxcd": "教室",
        "zcd": "周次",
        "xqj": 1,           // 星期（1-7）
        "ksj": 1,           // 开始节次
        "jsj": 2            // 结束节次
    }]
}
```

### 4.3 成绩查询

**请求**：
```
GET /student/pygl/xscjcx_list?_=<timestamp>
```

**响应**（AES 加密）：
```json
[{
    "kch": "课程编号",
    "kcmc": "课程名称",
    "cj": "90.0",          // 成绩
    "xf": "3.0",           // 学分
    "kcxz": "必修",        // 课程类型
    "xqmc": "2025年春季"   // 学期
}]
```

### 4.4 考试安排

**请求**：
```
POST /student/pygl/kckccx_list

Content-Type: application/x-www-form-urlencoded

{}
```

**响应**（AES 加密）：
```json
[{
    "termname": "25年秋季",     // 学期
    "kcmc": "矩阵理论",         // 课程名称
    "kcbh": "课程编号",
    "ksrq": "2026-01-06",      // 考试日期
    "kssj": "09:00-11:00",     // 考试时间
    "dz": "教学楼101",         // 地点
    "zwh": "25",               // 座位号
    "khxs": "笔试",            // 考试形式
    "zjjs": "主监考",          // 主监考
    "fjjs": "副监考",          // 副监考
    "ksrs": "30"               // 考试人数
}]
```

---

## 5. 数据流

```
用户输入
   │
   ▼
┌─────────────────────────────┐
│  RSA 加密密码               │
│  OCR 识别验证码             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  POST 登录请求              │
│  (带 Session ID)            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  接收 AES 加密响应          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  AES 解密 → JSON 解析       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  存储 Session/Cookie        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  发起 API 请求              │
│  (学生信息/课程表/成绩/考试) │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  接收并 AES 解密响应        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Pydantic 数据验证          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  TUI 渲染数据               │
└─────────────────────────────┘
```

---

## 6. 错误处理

### 6.1 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 登录失败 | 验证码错误 | 自动重试（最多3次） |
| 登录失败 | 密码错误 | 检查学号密码 |
| 未登录 | Session 失效 | 重新登录 |
| 解密失败 | AES 密钥不匹配 | 检查 `crypto.py` |
| 获取失败 | 网络错误 | 检查网络连接 |

### 6.2 重试机制

```python
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    try:
        # 尝试登录
        result = await login()
        if result['jg'] == '1':
            break
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise
        await asyncio.sleep(1)
```

---

## 7. 安全注意事项

1. **密钥保护**
   - RSA 公钥：从 HTML 动态获取，不硬编码
   - AES 密钥：硬编码在 `constants.py`（逆向结果）

2. **密码安全**
   - 使用 `getpass()` 安全输入
   - 可选 keyring 存储
   - 不记录日志

3. **网络安全**
   - 使用 HTTPS
   - Session 自动管理
   - 错误时清理敏感数据

---

## 8. 开发建议

### 8.1 调试技巧

1. 使用测试脚本单独测试功能
2. 打印中间结果查看加密/解密
3. 检查网络请求和响应
4. 验证 Session ID 是否正确

### 8.2 扩展功能

- 添加新的 API 端点
- 实现数据导出（CSV/Excel）
- 添加成绩统计
- 实现选课功能
- 添加考试提醒

### 8.3 性能优化

- 使用连接池
- 缓存学生信息
- 异步并发请求
- 减少不必要的 API 调用

---

## 9. 技术栈

- **HTTP**: httpx - 异步 HTTP 客户端
- **加密**: pycryptodome - AES/RSA 加密
- **验证码**: ddddocr - OCR 识别
- **TUI**: textual - 终端界面
- **验证**: pydantic - 数据模型
- **存储**: keyring - 密码存储

---

## 10. 许可证

MIT License - 仅供学习交流使用

---

**Made with ❤️ for WYU Graduate Students**