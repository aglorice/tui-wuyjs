"""登录流程"""
import json
import time
from typing import Optional, Callable

import httpx

from ..core.crypto import crypto_manager
from ..client.http_client import YJSClient
from .captcha import captcha_recognizer


class LoginManager:
    """登录管理器"""

    # 基础请求头（所有请求共享，确保User-Agent等参数一致）
    BASE_HEADERS = {
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Sec-Ch-Ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Site': 'same-origin',
    }

    def __init__(self, client: YJSClient):
        self.client = client

    def _build_headers(self, referer_url: str | None = None, **overrides) -> dict:
        """
        构建统一的请求头

        所有请求都使用相同的基础请求头（BASE_HEADERS），
        确保User-Agent等反爬虫关键参数一致。

        Args:
            referer_url: Referer URL（可选）
            **overrides: 覆盖或添加的额外请求头

        Returns:
            完整的请求头
        """
        headers = self.BASE_HEADERS.copy()

        # 添加Host
        headers['Host'] = 'yjsc.wyu.edu.cn'

        # 添加Referer（如果提供）
        if referer_url:
            headers['Referer'] = referer_url

        # 应用额外的覆盖
        headers.update(overrides)

        return headers

    def _build_captcha_headers(self, referer_url: str) -> dict:
        """
        构建验证码请求头

        Args:
            referer_url: 登录页面URL（包含Session ID）

        Returns:
            完整的请求头
        """
        return self._build_headers(
            referer_url=referer_url,
            **{
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
            }
        )

    def _build_login_headers(self, referer_url: str) -> dict:
        """
        构建登录POST请求头

        Args:
            referer_url: 登录页面URL（包含Session ID）

        Returns:
            完整的请求头
        """
        return self._build_headers(
            referer_url=referer_url,
            **{
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://yjsc.wyu.edu.cn',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'X-Requested-With': 'XMLHttpRequest',
            }
        )

    def _build_page_headers(self, referer_url: str | None = None) -> dict:
        """
        构建获取页面HTML的请求头（用于获取公钥等）

        Args:
            referer_url: Referer URL（可选）

        Returns:
            完整的请求头
        """
        return self._build_headers(
            referer_url=referer_url,
            **{
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
        )

    async def login(
        self,
        user_id: str,
        password: str,
        max_retries: int = 1,
        progress_callback: Optional[Callable] = None,
    ) -> dict:
        """
        登录

        根据 DOCUMENT.md 的登录流程：
        1. GET 首页 → 自动重定向到带 Session ID 的登录页（在 initialize() 中完成）
        2. 提取 Session ID（在 initialize() 中完成）
        3. 获取 RSA 公钥（在 initialize() 中完成，避免重复请求）
        4. 获取验证码（使用同一个Session和正确的请求头）
        5. 识别验证码
        6. RSA 加密密码（使用缓存的公钥）
        7. POST 登录请求

        Args:
            user_id: 学号
            password: 密码
            max_retries: 最大重试次数（验证码识别可能失败）

        Returns:
            登录响应
        """
        # 使用缓存的公钥（在initialize()时已获取）
        rsa_pubkey = self.client.rsa_pubkey

        for attempt in range(1, max_retries + 1):
            try:
                # 1. 构建登录页面URL（用于Referer）
                login_url = self.client.session.build_url('/home/stulogin')

                # 2. 构建验证码请求头（包含Referer，保持Session一致）
                captcha_headers = self._build_captcha_headers(login_url)

                # 3. 获取验证码 URL（带 Session ID 和时间戳）
                # 根据 DOCUMENT.md: GET /Home/VerificationCode?codetype=stucode&t=<timestamp>
                captcha_url = self.client.session.build_url('/Home/VerificationCode')
                timestamp = int(time.time() * 1000)
                full_captcha_url = f'{captcha_url}?codetype=stucode&t={timestamp}'

                # 4. 识别验证码（使用同一个client和正确的请求头）
                if progress_callback:
                    progress_callback(f"正在识别验证码...（第 {attempt} 次尝试）")

                captcha_code = await captcha_recognizer.recognize_from_url(
                    full_captcha_url,
                    client=self.client.session.client,  # 使用同一个client保持Session
                    headers=captcha_headers,            # 传递完整的请求头
                    show_image=False,                   # 不显示图片（调试时可改为True）
                    progress_callback=progress_callback # 传递进度回调
                )

                if not captcha_code:
                    error_msg = f"验证码识别失败（第 {attempt} 次尝试）"
                    if progress_callback:
                        progress_callback(error_msg, severity="warning")
                    if attempt < max_retries:
                        # 验证码识别失败，重试
                        continue
                    raise Exception("验证码识别失败")

                if progress_callback:
                    progress_callback(f"验证码识别成功: {captcha_code}", severity="information")

                # 6. RSA 加密密码（使用从HTML获取的动态公钥）
                encrypted_password = crypto_manager.rsa_encrypt_password(password, rsa_pubkey)

                # 7. 构造登录请求数据
                # 根据 DOCUMENT.md: json={"UserId":"学号","Password":"<RSA加密的密码>","VeriCode":"验证码","url":"","city":""}
                login_data = {
                    "UserId": user_id,
                    "Password": encrypted_password,
                    "VeriCode": captcha_code,
                    "url": "",
                    "city": "",
                }
                # 重要：将字典序列化为JSON字符串
                form_data = {
                    "json": json.dumps(login_data, ensure_ascii=False),
                }

                # 8. 构建登录POST请求头（包含正确的Referer和AJAX标识）
                login_headers = self._build_login_headers(login_url)

                # 9. 发送登录请求（使用正确的AJAX请求头）
                # POST /home/stulogin_do
                response = await self.client.post(
                    '/home/stulogin_do',
                    data=form_data,
                    headers=login_headers,  # 传递登录请求头
                )

                # 9. 检查登录结果
                # 响应格式: {"jg": "1", "url": "..."} 或 {"jg": "0", "msg": "错误信息"}
                if response.get('jg') == '1':
                    self.client.is_logged_in = True
                    return response
                else:
                    # 登录失败
                    error_msg = response.get('msg', '未知错误')
                    if attempt < max_retries:
                        # 验证码可能错误，重试
                        continue
                    raise Exception(f"登录失败: {error_msg}")

            except httpx.HTTPError as e:
                error_msg = f"网络请求失败: {str(e)}"
                if attempt < max_retries:
                    continue
                raise Exception(error_msg)
            except Exception as e:
                if attempt < max_retries:
                    continue
                raise

        raise Exception(f"登录失败，已重试 {max_retries} 次")

    async def logout(self):
        """登出"""
        self.client.is_logged_in = False