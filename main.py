"""YJS 教务系统工具 - 主入口"""

import asyncio
import logging
import sys
import warnings

# 在导入其他模块之前就抑制 onnxruntime 的警告
# 这些警告会被 Textual 捕获并干扰程序运行
logging.getLogger("onnxruntime").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*Expected shape from model.*")
warnings.filterwarnings("ignore", category=Warning)

# 重定向 stderr 到 null（可选，更激进的抑制方式）
# 注意：这会抑制所有 stderr 输出，包括正常的错误信息
# class StderrFilter:
#     def __init__(self):
#         self.original_stderr = sys.stderr
#         self.buffer = []
#
#     def write(self, text):
#         if "onnxruntime" not in text and "Expected shape from model" not in text:
#             self.original_stderr.write(text)
#
#     def flush(self):
#         self.original_stderr.flush()
#
# sys.stderr = StderrFilter()

from src.ui.app import YJSApp

logging.basicConfig(level=logging.WARNING)


def main():
    """主函数"""
    app = YJSApp()
    app.run()


if __name__ == "__main__":
    main()
