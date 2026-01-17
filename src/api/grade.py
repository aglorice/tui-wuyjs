"""成绩 API"""
import json
import time
from typing import Optional

from ..client.http_client import YJSClient
from .models import Grade


class GradeAPI:
    """成绩 API"""

    def __init__(self, client: YJSClient):
        self.client = client

    async def get_grades(self) -> list[Grade]:
        """
        获取成绩

        Returns:
            成绩列表
        """
        if not self.client.is_logged_in:
            raise Exception("未登录，请先登录")

        # 打印调试信息
        print(f"[DEBUG] 准备获取成绩，登录状态: {self.client.is_logged_in}")
        print(f"[DEBUG] Session ID: {self.client.session.session_id}")

        # 发送请求
        response = await self.client.get(
            '/student/pygl/xscjcx_list',
            params={'_': int(time.time() * 1000)},
        )
        # 解析响应
        grades = []
        all_courses = []

        # 检查响应类型
        if isinstance(response, dict):
            # 如果响应包含 raw 字段，说明解密失败
            if 'raw' in response:
                print(f"响应内容（未解密）: {response['raw'][:200]}")
                return grades
            # 正常格式: {"xwklist": [...], "fxwklist": [...], "xftj": {...}}
            xwklist = response.get('xwklist', [])  # 学位课列表
            fxwklist = response.get('fxwklist', [])  # 非学位课列表
            xftj = response.get('xftj', {})  # 学分统计

            # 合并两个列表
            for item in xwklist:
                item['course_type'] = '学位课'
                all_courses.append(item)
            for item in fxwklist:
                item['course_type'] = '非学位课'
                all_courses.append(item)

        elif isinstance(response, list):
            # 响应直接是一个列表
            print(f"[DEBUG] 响应是列表格式，包含 {len(response)} 项")
            all_courses = response
            for item in all_courses:
                item['course_type'] = '未知类型'
        else:
            print(f"未知的响应格式: {type(response)}")
            return grades


        # 解析数据
        for item in all_courses:
            # 尝试转换成绩，如果是"免修"等特殊值，处理为0
            score_str = item.get('cj', '0')
            try:
                score = float(score_str) if str(score_str).replace('.', '').isdigit() else 0.0
            except:
                score = 0.0

            grade = Grade(
                course_name=item.get('kcmc', ''),
                score=score,
                credit=float(item.get('kcxf', 0)),
                gpa=0.0,  # 响应中没有绩点字段
                semester=item.get('kkxq', ''),
                course_type=item.get('course_type', ''),
            )
            grades.append(grade)

        return grades