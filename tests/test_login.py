"""
简单的登录测试脚本

用于测试登录功能是否正常工作。
"""

import asyncio
import getpass

from src.auth.login import LoginManager
from src.client.http_client import YJSClient
from PIL import Image
# 补丁：兼容旧代码
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

async def test_login():
    """
    测试登录功能

    步骤：
    1. 获取用户输入的学号和密码
    2. 初始化客户端
    3. 尝试登录
    4. 显示结果
    """
    print("=" * 60)
    print("YJS 教务系统 - 登录功能测试")
    print("=" * 60)
    print()

    # 获取用户输入
    user_id = input("请输入学号: ").strip()
    password = getpass.getpass("请输入密码: ").strip()


    print()
    print("开始测试登录流程...")
    print("-" * 60)

    client = None
    try:
        # 初始化客户端
        print("1. 初始化客户端...")
        client = YJSClient()
        await client.initialize()
        print("   ✅ 客户端初始化成功 - ",client.session.session_id)
        # 创建登录管理器
        login_manager = LoginManager(client)
        # 尝试登录
        print("2. 开始登录...")
        result = await login_manager.login(user_id, password)
        print("   ✅ 登录成功！")
        print()
        print("-" * 60)
        print("登录结果:")
        print(f"   状态: {'✅ 成功' if result.get('jg') == '1' else '❌ 失败'}")
        if result.get('url'):
            print(f"   跳转URL: {result.get('url')}")
        print()
        print("=" * 60)
        print("🎉 登录功能正常工作！")
        print("=" * 60)

    except Exception as err:
        print()
        print("-" * 60)
        print("❌ 登录失败！")
        print(f"错误信息: {str(err)}")
        print()
        print("可能的原因:")
        print("  1. 学号或密码错误")
        print("  2. 网络连接问题")
        print("  3. 验证码识别失败（请重试）")
        print("  4. 服务器问题")
        print()
        print("建议: 多试几次，验证码识别可能需要重试")
        print("=" * 60)

    finally:
        # 关闭客户端
        if client:
            await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_login())
    except KeyboardInterrupt:
        print()
        print("\n用户取消操作")
    except Exception as e:
        print()
        print(f"\n发生未预期的错误: {str(e)}")