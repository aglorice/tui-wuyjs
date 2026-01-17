"""HTTP 客户端封装"""

import html
import json
import re
from typing import Any

import httpx

from ..core.crypto import crypto_manager
from .session import SessionManager


class YJSClient:
    """教务系统 HTTP 客户端"""

    def __init__(self):
        self.session = SessionManager()
        self._is_logged_in = False
        self._rsa_pubkey: str | None = None  # RSA公钥缓存

    async def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        """
        发送 GET 请求

        Args:
            path: 请求路径
            params: 查询参数

        Returns:
            解密后的 JSON 响应
        """
        url = self.session.build_url(path)
        response = await self.session.client.get(url, params=params)
        return self._decrypt_response(response)

    async def post(
        self,
        path: str,
        data: dict | None = None,
        json_data: dict | None = None,
        headers: dict | None = None,
    ) -> dict[str, Any]:
        """
        发送 POST 请求

        Args:
            path: 请求路径
            data: 表单数据
            json_data: JSON 数据
            headers: 自定义请求头

        Returns:
            解密后的 JSON 响应
        """
        url = self.session.build_url(path)

        if json_data:
            response = await self.session.client.post(url, headers=headers, json=json.dumps(json_data))
        else:
            response = await self.session.client.post(url, data=data, headers=headers)
        return self._decrypt_response(response)

    def _decrypt_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        解密响应

        Args:
            response: HTTP 响应

        Returns:
            解密后的 JSON 数据
        """
        # 获取响应文本
        ciphertext = response.text
        # 尝试解密
        try:
            plaintext = crypto_manager.aes_decrypt_response(ciphertext)
            # 尝试解析 JSON
            return json.loads(plaintext)
        except (json.JSONDecodeError, Exception):
            # 解密失败或不是 JSON，返回原始文本
            return {'raw': ciphertext}

    async def _get_session_and_pubkey(self) -> tuple[str, str]:
        """
        一次请求同时获取 Session ID 和 RSA 公钥

        访问首页，自动重定向到登录页，同时提取：
        1. Session ID（从重定向后的URL）
        2. RSA 公钥（从HTML中）

        Returns:
            (session_id, rsa_pubkey)
        """
        from ..core.constants import BASE_URL

        # 使用页面请求头
        page_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Host': 'yjsc.wyu.edu.cn',
        }

        # 访问首页，自动重定向到带Session ID的登录页
        response = await self.session.client.get(BASE_URL, headers=page_headers)

        # 1. 从重定向后的 URL 提取 Session ID
        # URL 格式: https://yjsc.wyu.edu.cn/(S(abc123))/home/stulogin
        import re
        session_match = re.search(r'\(S\(([^)]+)\)\)', str(response.url))
        if not session_match:
            raise Exception(f"无法获取 Session ID，重定向到: {response.url}")
        session_id = session_match.group(1)

        # 2. 从HTML中提取RSA公钥
        html_content = response.text
        pattern = r'<input\s+id="pubkey"[^>]*value=([\'"])(.*?)\1'
        match = re.search(pattern, html_content, re.S)

        if not match:
            raise Exception("无法从登录页面获取RSA公钥")

        content = match.group(2)
        # HTML实体解码
        pubkey = html.unescape(content)

        return session_id, pubkey

    async def initialize(self):
        """
        初始化 Session 和 RSA 公钥

        一次请求同时完成：
        1. 获取 Session ID
        2. 获取 RSA 公钥
        """
        # 一次请求同时获取 Session ID 和 RSA 公钥
        session_id, pubkey = await self._get_session_and_pubkey()

        # 设置 Session ID
        self.session.session_id = session_id

        # 缓存 RSA 公钥
        self._rsa_pubkey = pubkey

        print(f"✅ 初始化完成")
        print(f"   Session ID: {session_id}")
        print(f"   RSA公钥长度: {len(pubkey)} 字符")

    @property
    def rsa_pubkey(self) -> str:
        """
        获取RSA公钥

        Returns:
            RSA公钥（PEM格式）

        Raises:
            Exception: 如果公钥未初始化
        """
        if not self._rsa_pubkey:
            raise Exception("RSA公钥未初始化，请先调用 initialize()")
        return self._rsa_pubkey

    async def close(self):
        """关闭客户端"""
        await self.session.close()

    def get_current_cookies(self) -> dict[str, str]:
        """
        获取当前所有cookies

        Returns:
            cookies字典
        """
        return self.session.get_cookies()

    @property
    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self._is_logged_in

    @is_logged_in.setter
    def is_logged_in(self, value: bool):
        """设置登录状态"""
        self._is_logged_in = value

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()