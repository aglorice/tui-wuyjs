"""
测试 API 功能

用于测试登录后获取成绩和课程表的功能。
"""

import asyncio
import getpass

from src.auth.login import LoginManager
from src.client.http_client import YJSClient
from src.api.grade import GradeAPI
from src.api.course import CourseAPI
from PIL import Image

# 补丁：兼容旧代码
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


async def test_api():
    """
    测试 API 功能

    步骤：
    1. 获取用户输入的学号和密码
    2. 初始化客户端
    3. 登录
    4. 获取成绩
    5. 获取课程表
    6. 显示结果
    """
    print("=" * 60)
    print("YJS 教务系统 - API 功能测试")
    print("=" * 60)
    print()

    # 获取用户输入
    user_id = input("请输入学号: ").strip()
    password = getpass.getpass("请输入密码: ").strip()

    print()
    print("开始测试 API 功能...")
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

        # 3. 获取成绩
        print("3. 获取成绩...")
        grade_api = GradeAPI(client)
        grades = await grade_api.get_grades()

        if grades:
            print(f"   ✅ 成功获取 {len(grades)} 条成绩记录")
            print()
            print("   成绩列表:")
            print("   " + "-" * 80)
            print(f"   {'课程名称':<25} {'成绩':<8} {'学分':<6} {'课程类型':<10} {'学期':<12}")
            print("   " + "-" * 80)
            for grade in grades:
                score_str = f"{grade.score:.1f}" if grade.score > 0 else "免修"
                print(f"   {grade.course_name:<25} {score_str:<8} {grade.credit:<6.1f} "
                      f"{grade.course_type:<10} {grade.semester:<12}")
            print("   " + "-" * 80)
        else:
            print("   ⚠️  暂无成绩数据")
        print()

        # 4. 获取课程表
        print("4. 获取课程表...")
        course_api = CourseAPI(client)
        courses = await course_api.get_courses()

        if courses:
            print(f"   ✅ 成功获取 {len(courses)} 条课程记录")
            print()
            print("   课程表:")
            print("   " + "-" * 90)
            print(f"   {'课程名称':<20} {'教师':<10} {'教室':<15} {'周次':<10} {'星期':<6} {'节次':<10}")
            print("   " + "-" * 90)
            for course in courses:
                print(f"   {course.course_name:<20} {course.teacher:<10} {course.classroom:<15} "
                      f"{course.week:<10} {str(course.day):<6} {course.start_node}-{course.end_node:<5}")
            print("   " + "-" * 90)
        else:
            print("   ⚠️  暂无课程数据")
        print()

        print("=" * 60)
        print("🎉 API 功能测试完成！")
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
        asyncio.run(test_api())
    except KeyboardInterrupt:
        print()
        print("\n用户取消操作")
    except Exception as e:
        print()
        print(f"\n发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()