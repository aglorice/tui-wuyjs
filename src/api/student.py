"""学生信息 API"""

import time
from typing import Optional

from ..client.http_client import YJSClient
from .models import StudentInfo


class StudentInfoAPI:
    """学生信息 API"""

    def __init__(self, client: YJSClient):
        self.client = client

    async def get_student_info(self) -> Optional[StudentInfo]:
        """
        获取学生基本信息

        Returns:
            学生信息对象，如果获取失败返回 None
        """
        if not self.client.is_logged_in:
            raise Exception("未登录，请先登录")

        try:
            # GET /student/default/getxscardinfo
            response = await self.client.get(
                '/student/default/getxscardinfo',
                params={'_': int(time.time() * 1000)},
            )

            # 解析响应
            data = None

            if isinstance(response, dict):
                if 'raw' in response:
                    # 解密失败
                    print(f"响应内容（未解密）: {response['raw'][:200]}")
                    return None
                data = response
            elif isinstance(response, list):
                # 如果返回的是列表，取第一个元素
                if len(response) > 0:
                    data = response[0]
                else:
                    return None
            else:
                print(f"未知的响应格式: {type(response)}")
                return None

            if not data:
                return None

            # 构建学生信息模型
            student_info = StudentInfo(
                student_id=data.get('xh', ''),
                name=data.get('xm', ''),
                college=data.get('xsmc', ''),
                major=data.get('zymc', ''),
                student_type=data.get('xslb', ''),
                advisor=data.get('dsxm', ''),
                advisor1=data.get('dsxm1', ''),
                advisor2=data.get('dsxm2', ''),
                advisor3=data.get('dsxm3', ''),
                grade=data.get('nj', ''),
                advisor_info=data.get('dsinfo', ''),
            )

            print(f"成功获取学生信息: {student_info.name} ({student_info.student_id})")
            return student_info

        except Exception as e:
            print(f"获取学生信息失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None