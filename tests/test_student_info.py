"""
测试学生信息查询功能

用于测试登录后获取学生基本信息的功能。
"""

import asyncio
import getpass

from src.auth.login import LoginManager
from src.client.http_client import YJSClient
from src.api.student import StudentInfoAPI
from PIL import Image

# 补丁：兼容旧代码
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


async def test_student_info_api():
    """
    测试学生信息查询API功能

    步骤：
    1. 获取用户输入的学号和密码
    2. 初始化客户端
    3. 登录
    4. 获取学生信息
    5. 显示结果
    """
    print("=" * 60)
    print("YJS 教务系统 - 学生信息查询功能测试")
    print("=" * 60)
    print()

    # 获取用户输入
    import getpass
    user_id = input("请输入学号: ").strip()
    password = getpass.getpass("请输入密码: ").strip()

    print()
    print("开始测试学生信息查询API...")
    print("-" * 60)

    client = None
    try:
        # 1. 初始化客户端
        print("1. 初始化客户端...")
        client = YJSClient()
        await client.initialize()
        print(f"   ✅ 客户端初始化成功")
        print(f"   Session ID: {client.session.session_id}")
        print()

        # 2. 登录
        print("2. 登录...")
        login_manager = LoginManager(client)
        result = await login_manager.login(user_id, password)
        print("   ✅ 登录成功！")
        print()

        # 3. 获取学生信息
        print("3. 获取学生信息...")
        student_api = StudentInfoAPI(client)
        student_info = await student_api.get_student_info()

        if student_info:
            print(f"   ✅ 成功获取学生信息")
            print()
            print("   学生信息详情:")
            print("   " + "-" * 60)

            # 打印所有字段
            for key, value in student_info.items():
                print(f"   {key:<30}: {value}")

            print("   " + "-" * 60)
        else:
            print("   ⚠️  未获取到学生信息")
        print()

        print("=" * 60)
        print("🎉 学生信息查询功能测试完成！")
        print("=" * 60)
        print()
        print("请将上方的返回数据发送给开发者，以便设计UI界面")

    except Exception as err:
        print()
        print("-" * 60)
        print("❌ 测试失败！")
        print(f"错误信息: {str(err)}")
        print()
        print("可能的原因:")
        print("  1. 学号或密码错误")
        print("  2. 网络连接问题")
        print("  3. 验证码识别失败（请重试）")
        print("  4. 服务器问题")
        print("  5. 未登录或登录状态失效")
        print()
        print("建议: 多试几次，验证码识别可能需要重试")
        print("=" * 60)

    finally:
        # 关闭客户端
        if client:
            await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_student_info_api())
    except KeyboardInterrupt:
        print()
        print("\n用户取消操作")
    except Exception as e:
        print()
        print(f"\n发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()