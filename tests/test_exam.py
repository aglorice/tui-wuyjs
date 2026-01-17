"""
测试考试查询功能

用于测试登录后获取考试信息的功能。
"""

import asyncio
import getpass

from src.auth.login import LoginManager
from src.client.http_client import YJSClient
from src.api.exam import ExamAPI
from PIL import Image

# 补丁：兼容旧代码
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


async def test_exam_api():
    """
    测试考试查询API功能

    步骤：
    1. 获取用户输入的学号和密码
    2. 初始化客户端
    3. 登录
    4. 获取考试信息
    5. 显示结果
    """
    print("=" * 60)
    print("YJS 教务系统 - 考试查询功能测试")
    print("=" * 60)
    print()

    # 获取用户输入
    import getpass
    user_id = input("请输入学号: ").strip()
    password = getpass.getpass("请输入密码: ").strip()

    print()
    print("开始测试考试查询API...")
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

        # 3. 获取考试信息
        print("3. 获取考试信息...")
        exam_api = ExamAPI(client)
        exams = await exam_api.get_exams()

        if exams:
            print(f"   ✅ 成功获取 {len(exams)} 条考试记录")
            print()
            print("   考试列表:")
            print("   " + "-" * 120)
            print(f"   {'课程名称':<20} {'课程编号':<10} {'学期':<10} {'日期':<12} {'时间':<12} {'地点':<20} {'座位':<6} {'考试形式':<12} {'监考老师':<15}")
            print("   " + "-" * 120)
            for exam in exams:
                teachers = f"{exam.main_teacher}" if exam.main_teacher else ""
                if exam.assistant_teacher:
                    teachers += f"、{exam.assistant_teacher}" if teachers else exam.assistant_teacher

                print(f"   {exam.course_name:<20} {exam.course_code:<10} {exam.term_name:<10} "
                      f"{exam.exam_date:<12} {exam.exam_time:<12} {exam.classroom:<20} {exam.seat_number:<6} "
                      f"{exam.exam_type:<12} {teachers:<15}")
            print("   " + "-" * 120)
        else:
            print("   ⚠️  暂无考试数据")
        print()

        print("=" * 60)
        print("🎉 考试查询功能测试完成！")
        print("=" * 60)

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
        asyncio.run(test_exam_api())
    except KeyboardInterrupt:
        print()
        print("\n用户取消操作")
    except Exception as e:
        print()
        print(f"\n发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()