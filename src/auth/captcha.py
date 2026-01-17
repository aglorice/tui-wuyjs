"""验证码识别"""

import io
import logging
import os
import sys
import warnings
from contextlib import contextmanager
from typing import Optional, Callable

import ddddocr
import httpx
from PIL import Image
# 补丁：兼容旧代码
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
# 抑制 onnxruntime 的警告输出
# 这些警告会在 TUI 中被捕获并干扰程序运行
logging.getLogger("onnxruntime").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*Expected shape from model.*")


@contextmanager
def suppress_stderr():
    """临时抑制 stderr 输出"""
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr


class CaptchaRecognizer:
    """验证码识别器"""

    def __init__(self):
        # 初始化 OCR（不使用 suppress_stderr，可能在 TUI 环境中有问题）
        try:
            self.ocr = ddddocr.DdddOcr()
            print(f"[验证码] OCR 初始化成功")
        except Exception as e:
            print(f"[验证码] OCR 初始化失败: {str(e)}")
            # 即使初始化失败也创建实例，延迟到首次使用时再处理
            self.ocr = None

    async def download_captcha(
        self,
        url: str,
        client: httpx.AsyncClient | None = None,
        headers: dict | None = None
    ) -> bytes:
        """
        下载验证码图片

        Args:
            url: 验证码图片 URL
            client: HTTP客户端（如果提供则使用该客户端，否则创建新的）
            headers: 请求头（用于保持Session一致）

        Returns:
            图片数据
        """
        if client:
            # 使用提供的客户端（保持Session一致）
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        else:
            # 创建新客户端（向后兼容）
            async with httpx.AsyncClient() as new_client:
                response = await new_client.get(url, headers=headers)
                response.raise_for_status()
                return response.content

    async def recognize(self, image_bytes: bytes, progress_callback: Optional[Callable] = None) -> str:
        """
        识别验证码

        Args:
            image_bytes: 图片数据
            progress_callback: 进度回调函数

        Returns:
            识别结果
        """
        # 检查 OCR 是否已初始化
        if self.ocr is None:
            msg = "[验证码识别] OCR 未初始化，尝试重新初始化"
            print(msg)
            if progress_callback:
                progress_callback(msg)
            try:
                self.ocr = ddddocr.DdddOcr()
                msg = "[验证码识别] OCR 重新初始化成功"
                print(msg)
                if progress_callback:
                    progress_callback(msg)
            except Exception as e:
                msg = f"[验证码识别] OCR 初始化失败: {str(e)}"
                print(msg)
                if progress_callback:
                    progress_callback(msg, severity="error")
                return ''

        try:
            # 尝试识别，即使有警告也继续
            result = self.ocr.classification(image_bytes)

            # 打印调试信息（帮助诊断）
            msg = f"[验证码识别] 原始结果: '{result}' (类型: {type(result)})"
            print(msg)
            if progress_callback:
                progress_callback(msg)

            # 检查结果
            if result and isinstance(result, str) and len(result) >= 3:
                # 清理结果（只保留数字和字母）
                cleaned = ''.join(c for c in result if c.isalnum())
                msg = f"[验证码识别] 清理后结果: '{cleaned}'"
                print(msg)
                if progress_callback:
                    progress_callback(msg)
                return cleaned
            else:
                msg = f"[验证码识别] 结果无效或为空"
                print(msg)
                if progress_callback:
                    progress_callback(msg, severity="warning")
                return ''
        except Exception as e:
            # 识别异常，打印详细错误
            import traceback
            msg = f"[验证码识别] 异常: {str(e)}"
            print(msg)
            print(f"[验证码识别] 异常类型: {type(e).__name__}")
            traceback.print_exc()
            if progress_callback:
                progress_callback(msg, severity="error")
            return ''

    async def recognize_from_url(
        self,
        url: str,
        client: httpx.AsyncClient | None = None,
        headers: dict | None = None,
        show_image: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        从 URL 下载并识别验证码

        Args:
            url: 验证码图片 URL
            client: HTTP客户端（用于保持Session一致）
            headers: 请求头
            show_image: 是否显示验证码图片
            progress_callback: 进度回调函数

        Returns:
            识别结果
        """
        if progress_callback:
            progress_callback("正在下载验证码图片...")

        image_bytes = await self.download_captcha(url, client, headers)

        if progress_callback:
            progress_callback("正在识别验证码...")

        # 可选：展示验证码（调试用）
        if show_image:
            try:
                image = Image.open(io.BytesIO(image_bytes))
                image.show()
            except Exception as e:
                print(f"展示图片失败: {e}")

        return await self.recognize(image_bytes, progress_callback=progress_callback)


# 全局单例
captcha_recognizer = CaptchaRecognizer()