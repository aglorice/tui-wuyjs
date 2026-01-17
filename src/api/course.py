"""课程表 API"""

import time
import re
from typing import Optional

from ..client.http_client import YJSClient
from .models import Course


class CourseAPI:
    """课程表 API"""

    def __init__(self, client: YJSClient):
        self.client = client

    async def get_terms(self) -> list[dict]:
        """
        获取学期列表

        Returns:
            学期列表
        """
        if not self.client.is_logged_in:
            raise Exception("未登录")

        # 发送请求获取学期列表
        response = await self.client.get(
            '/student/default/bindterm',
            params={'_': int(time.time() * 1000)},
        )

        # 解析响应
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and 'raw' in response:
            print(f"响应内容（未解密）: {response['raw'][:200]}")
            return []
        else:
            return []

    def _parse_course_info(self, course_str: str) -> dict:
        """
        解析课程信息字符串

        Args:
            course_str: 课程信息字符串，格式：课程名<br/>专业<br/>[周次]<br/> 教师[教室]

        Returns:
            包含课程名、教师、教室、周次的字典
        """
        if not course_str or course_str == 'None':
            return None

        # 替换 <br/> 为换行符，方便处理
        text = course_str.replace('<br/>', '\n')

        # 分割行
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not lines:
            return None

        # 第一行是课程名称
        course_name = lines[0]

        # 最后一行通常是 "教师[教室]" 格式
        teacher = ''
        classroom = ''

        if len(lines) > 1:
            last_line = lines[-1]
            # 提取教师和教室：教师姓名[教室]
            match = re.search(r'([^\[]+)\[([^\]]+)\]', last_line)
            if match:
                teacher = match.group(1).strip()
                classroom = match.group(2).strip()

        # 提取周次信息（通常在方括号中）
        week = ''
        for line in lines:
            if '周' in line:
                week = line.strip()
                break

        return {
            'course_name': course_name,
            'teacher': teacher,
            'classroom': classroom,
            'week': week,
            'raw': course_str
        }

    async def get_courses(self, term_id: Optional[str] = None) -> list[Course]:
        """
        获取课程表

        Args:
            term_id: 学期ID（可选，如果不提供则使用默认学期47）

        Returns:
            课程列表
        """
        if not self.client.is_logged_in:
            raise Exception("未登录")

        # 如果没有提供学期ID，使用默认值
        if term_id is None:
            term_id = "47"

        try:
            # 使用正确的课程表API endpoint
            # POST /student/pygl/py_kbcx_ew
            # 参数: kblx=xs (课表类型=学生), termcode=47 (学期代码)
            response = await self.client.post(
                '/student/pygl/py_kbcx_ew',
                data={'kblx': 'xs', 'termcode': term_id}
            )

            # 解析响应
            courses = []

            if isinstance(response, dict) and 'rows' in response:
                rows = response['rows']
            elif isinstance(response, list):
                rows = response
            else:
                print(f"未知的响应格式: {type(response)}")
                return []

            # 打印原始数据用于调试
            if rows:
                print(f"获取到 {len(rows)} 行课程表数据")
            else:
                print("未获取到课程数据")

            # 解析课程表矩阵
            for row in rows:
                # mc 是节次号 (1-11)
                period = row.get('mc', '')

                # 跳过"无节次"行
                if period == '无节次' or not period.isdigit():
                    continue

                period_num = int(period)

                # z1-z7 代表周日到周六 (1-7)
                for day in range(1, 8):  # 1-7
                    day_key = f'z{day}'
                    course_str = row.get(day_key, '')

                    if course_str and course_str != 'None':
                        # 解析课程信息
                        course_info = self._parse_course_info(course_str)

                        if course_info:
                            try:
                                # 计算节次：1-2节是period=1, 3-4节是period=2, 等等
                                start_node = (period_num - 1) * 2 + 1
                                end_node = period_num * 2

                                course = Course(
                                    course_name=course_info['course_name'],
                                    teacher=course_info['teacher'],
                                    classroom=course_info['classroom'],
                                    week=course_info['week'],
                                    day=day,  # 1-7 代表周一到周日
                                    start_node=start_node,
                                    end_node=end_node,
                                )
                                courses.append(course)
                            except (ValueError, TypeError) as e:
                                print(f"解析课程数据失败: {course_info}, 错误: {e}")
                                continue

            print(f"成功解析 {len(courses)} 门课程")
            return courses

        except Exception as e:
            print(f"获取课程表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []