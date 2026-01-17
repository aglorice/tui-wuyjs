"""数据模型"""

from pydantic import BaseModel


class Course(BaseModel):
    """课程信息"""

    course_name: str
    teacher: str
    classroom: str
    week: str
    day: int
    start_node: int
    end_node: int


class Grade(BaseModel):
    """成绩信息"""

    course_name: str
    score: float
    credit: float
    gpa: float
    semester: str
    course_type: str = ""  # 课程类型（必修/选修）


class Exam(BaseModel):
    """考试信息"""

    course_name: str  # 课程名称
    course_code: str = ""  # 课程编号
    term_name: str = ""  # 学期名称
    class_name: str = ""  # 班级名称
    exam_date: str = ""  # 考试日期
    exam_time: str = ""  # 考试时间
    classroom: str = ""  # 考试地点
    seat_number: str = ""  # 座位号
    exam_type: str = ""  # 考试形式（笔试/报告等）
    main_teacher: str = ""  # 主监考教师
    assistant_teacher: str = ""  # 副监考教师
    exam_count: str = ""  # 考试人数


class StudentInfo(BaseModel):
    """学生基本信息"""

    student_id: str = ""  # 学号 (xh)
    name: str = ""  # 姓名 (xm)
    college: str = ""  # 学院名称 (xsmc)
    major: str = ""  # 专业名称 (zymc)
    student_type: str = ""  # 学生类别 (xslb)
    advisor: str = ""  # 导师姓名 (dsxm)
    advisor1: str = ""  # 导师1 (dsxm1)
    advisor2: str = ""  # 导师2 (dsxm2)
    advisor3: str = ""  # 导师3 (dsxm3)
    grade: str = ""  # 年级 (nj)
    advisor_info: str = ""  # 导师信息 (dsinfo)