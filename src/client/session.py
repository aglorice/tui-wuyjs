"""Session 管理"""

import re
from urllib.parse import urljoin

import httpx

from ..core.constants import BASE_URL, TIMEOUT


class SessionManager:
    """Session 管理器"""

    # 默认请求头（所有请求共享，确保反爬虫参数一致）
    DEFAULT_HEADERS = {
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Sec-Ch-Ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Site': 'same-origin',
    }

    def __init__(self):
        # 创建带cookie持久化和默认请求头的AsyncClient
        # 所有请求都会自动携带这些默认请求头
        self.client = httpx.AsyncClient(
            timeout=TIMEOUT,
            follow_redirects=True,
            cookies=httpx.Cookies(),  # 显式创建cookie jar
            headers=self.DEFAULT_HEADERS,  # 设置默认请求头
        )
        self.session_id: str | None = None

    async def get_session_id(self) -> str:
        """
        获取 Session ID

        流程：
        1. GET 首页
        2. 自动重定向到带 Session ID 的登录页
        3. 提取 Session ID
        4. Cookies会自动保存到client.cookies中

        Returns:
            Session ID
        """
        # 访问首页
        response = await self.client.get(BASE_URL)

        # 从重定向后的 URL 提取 Session ID
        # URL 格式: https://yjsc.wyu.edu.cn/(S(abc123))/home/stulogin
        match = re.search(r'\(S\(([^)]+)\)\)', str(response.url))
        if match:
            self.session_id = match.group(1)
            return self.session_id

        raise Exception(f"无法获取 Session ID，重定向到: {response.url}")
        # 在 SessionManager 类中添加

    def update_session_id_from_url(self, url: str):
        """从 URL 中提取并更新 Session ID"""
        match = re.search(r'\(S\(([^)]+)\)\)', str(url))
        if match:
            new_id = match.group(1)
            if new_id != self.session_id:
                print(f"检测到 Session ID 变更: {self.session_id} -> {new_id}")
                self.session_id = new_id
    def build_url(self, path: str) -> str:
        """
        构建带 Session ID 的完整 URL

        Args:
            path: 路径（如 /student/default/bindterm）

        Returns:
            完整 URL（包含 Session ID）
        """
        if not self.session_id:
            raise Exception("Session ID 未初始化")
        if self.session_id is None:
            self.update_session_id_from_url(BASE_URL + path)
        # 插入 Session ID 到路径中
        # /student/default/bindterm -> /(S(session_id))/student/default/bindterm
        session_path = f"/(S({self.session_id})){path}"
        return urljoin(BASE_URL, session_path)

    def get_cookies(self) -> dict[str, str]:
        """
        获取当前所有cookies

        Returns:
            cookies字典
        """
        # httpx.Cookies的行为类似于dict
        return dict(self.client.cookies)

    def get_cookie(self, name: str) -> str | None:
        """
        获取指定cookie的值

        Args:
            name: cookie名称

        Returns:
            cookie值，如果不存在返回None
        """
        # httpx.Cookies支持dict-like访问
        return self.client.cookies.get(name)

    def set_cookie(self, name: str, value: str, domain: str = "yjsc.wyu.edu.cn"):
        """
        设置cookie

        Args:
            name: cookie名称
            value: cookie值
            domain: cookie域
        """
        self.client.cookies.set(name, value, domain=domain)

    def clear_cookies(self):
        """清除所有cookies"""
        self.client.cookies.clear()

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()