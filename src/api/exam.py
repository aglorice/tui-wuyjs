"""考试查询 API"""

import time
from typing import Optional

from ..client.http_client import YJSClient
from .models import Exam


class ExamAPI:
    """考试查询 API"""

    def __init__(self, client: YJSClient):
        self.client = client

    async def get_exams(self) -> list[Exam]:
        """
        获取考试信息

        Returns:
            考试列表
        """
        if not self.client.is_logged_in:
            raise Exception("未登录")

        try:
            # POST /student/pygl/kckccx_list
            response = await self.client.post(
                '/student/pygl/kckccx_list',
                data={}
            )

            # 解析响应
            exams = []

            if isinstance(response, list):
                data = response
            elif isinstance(response, dict):
                if 'raw' in response:
                    # 解密失败
                    print(f"响应内容（未解密）: {response['raw'][:200]}")
                    return []
                # 尝试多种可能的字段名
                data = (response.get('data', []) or
                       response.get('rows', []) or
                       response.get('list', []) or
                       response.get('exams', []))
            else:
                print(f"未知的响应格式: {type(response)}")
                return []

            # 打印原始数据用于调试
            if data:
                print(f"获取到 {len(data)} 条考试数据")
            else:
                print("未获取到考试数据")

            for item in data:
                # 根据实际返回字段映射
                try:
                    exam = Exam(
                        course_name=item.get('kcmc', ''),  # 课程名称
                        course_code=item.get('kcbh', ''),  # 课程编号
                        term_name=item.get('termname', ''),  # 学期名称
                        class_name=item.get('bjmc', ''),  # 班级名称
                        exam_date=item.get('ksrq', ''),  # 考试日期
                        exam_time=item.get('kssj', ''),  # 考试时间
                        classroom=item.get('dz', ''),  # 考试地点
                        seat_number=item.get('zwh', ''),  # 座位号
                        exam_type=item.get('khxs', ''),  # 考试形式
                        main_teacher=item.get('zjjs', '') or '',  # 主监考教师
                        assistant_teacher=item.get('fjjs', '') or '',  # 副监考教师
                        exam_count=str(item.get('ksrs', '')),  # 考试人数
                    )
                    exams.append(exam)
                except (ValueError, TypeError) as e:
                    print(f"解析考试数据失败: {item}, 错误: {e}")
                    continue

            print(f"成功解析 {len(exams)} 条考试信息")
            return exams

        except Exception as e:
            print(f"获取考试信息失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []