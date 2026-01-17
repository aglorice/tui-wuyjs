"""仪表盘界面 - 登录后的主界面"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Grid
from textual.screen import Screen
from textual.widgets import (
    Button,
    Header,
    Footer,
    Label,
    DataTable,
)


class DashboardScreen(Screen):
    """仪表盘界面 - 显示学生信息、成绩、课程表"""

    CSS = """
    Screen {
        background: $panel;
        layout: vertical;
    }

    #dashboard_header {
        height: 3;
        background: $primary;
        color: $text;
        text-style: bold;
        padding: 1;
        content-align: center middle;
    }

    #student_info {
        height: 7;
        border: thick $accent;
        background: $boost;
        padding: 1;
        margin: 1 2;
    }

    #student_info Horizontal {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }

    #student_info Label {
        width: 1fr;
    }

    .info_label {
        width: 12;
        text-style: bold;
        color: $accent;
        content-align: right middle;
    }

    .info_value {
        width: 40;
        text-style: italic;
        color: $text;
    }

    #main_content {
        height: 1fr;
        width: 1fr;
        margin: 0 2;
    }

    #sidebar {
        width: 25;
        border: thick $primary;
        background: $surface;
        padding: 1;
        margin: 0 1 0 0;
    }

    #sidebar Button {
        width: 1fr;
        margin: 0 0 1 0;
        min-height: 3;
    }

    #sidebar Button:hover {
        background: $primary;
        text-style: bold;
    }

    #sidebar Button.-primary {
        background: $primary;
        text-style: bold;
    }

    #content_area {
        height: 1fr;
        width: 1fr;
        border: thick $primary;
        background: $panel;
        margin: 0 0 0 1;
    }

    DataTable {
        width: 1fr;
        height: 1fr;
        background: $panel;
    }

    DataTable > DataTableHeader {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    DataTable > DataTableHeader > DataTableHeaderCell {
        background: $primary;
        color: $text;
        text-style: bold;
        border: solid $accent;
    }

    DataTable > DataTableCursor {
        background: $accent;
        text-style: bold;
    }

    #bottom_actions {
        height: auto;
        min-height: 3;
        margin: 1 2;
        background: $surface;
        border: round $primary;
        padding: 1;
    }

    #bottom_actions Button {
        width: 20;
        margin: 0 1;
        min-width: 16;
    }

    #bottom_actions Button:hover {
        text-style: bold;
    }

    #bottom_actions Button.-success {
        background: $success;
    }

    #bottom_actions Button.-error {
        background: $error;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_mode = "grades"  # grades, courses, exams
        self._is_switching = False  # 防止重复切换

    def on_mount(self) -> None:
        """界面加载时自动获取数据"""
        self.run_worker(self._load_all_data())

    async def _load_all_data(self) -> None:
        """加载所有数据"""
        try:
            # 加载学生信息
            await self._load_student_info()

            # 只加载当前可见的表格数据
            # 初始只显示成绩表
            await self._load_grades()

            self.app.notify("数据加载完成", severity="information")

        except Exception as e:
            self.app.notify(f"加载数据失败: {str(e)}", severity="error")

    async def _load_student_info(self) -> None:
        """加载学生基本信息"""
        from ...api.student import StudentInfoAPI

        try:
            # 调用 API 获取学生信息
            student_api = StudentInfoAPI(self.app.client)
            student_info = await student_api.get_student_info()

            if not student_info:
                # 如果获取失败，显示错误
                self.app.notify("获取学生信息失败", severity="error")
                return

            info_container = self.query_one("#student_info", Vertical)

            # 清空现有内容
            await info_container.remove_children()

            # 组合导师信息（如果有多个导师）
            advisors = [student_info.advisor]
            if student_info.advisor1:
                advisors.append(student_info.advisor1)
            if student_info.advisor2:
                advisors.append(student_info.advisor2)
            if student_info.advisor3:
                advisors.append(student_info.advisor3)
            advisor_str = "、".join([a for a in advisors if a])

            # 添加学生信息（两列布局）
            info_data = [
                ("学号:", student_info.student_id, "姓名:", student_info.name),
                ("学院:", student_info.college, "专业:", student_info.major),
                ("类别:", student_info.student_type, "年级:", student_info.grade),
            ]

            # 如果有导师信息，添加一行
            if advisor_str:
                info_data.append(("导师:", advisor_str, "", ""))

            for row_data in info_data:
                children = []
                for i in range(0, len(row_data), 2):
                    if i + 1 < len(row_data) and row_data[i]:  # 确保有数据
                        label = Label(row_data[i], classes="info_label")
                        value = Label(row_data[i + 1], classes="info_value")
                        children.extend([label, value])
                row = Horizontal(*children)
                await info_container.mount(row)

        except Exception as e:
            self.app.notify(f"加载学生信息失败: {str(e)}", severity="error")

    async def _load_grades(self) -> None:
        """加载成绩数据"""
        from ...api.grade import GradeAPI

        try:
            grade_api = GradeAPI(self.app.client)
            grades = await grade_api.get_grades()

            # 获取成绩表格
            grade_table = self.query_one("#grade_table", DataTable)

            # 清空现有数据（保留列）
            grade_table.clear()

            # 如果还没有列，添加列
            if not grade_table.columns:
                grade_table.add_column("课程名称", key="course_name", width=30)
                grade_table.add_column("成绩", key="score", width=10)
                grade_table.add_column("学分", key="credit", width=8)
                grade_table.add_column("课程类型", key="course_type", width=12)
                grade_table.add_column("学期", key="semester", width=12)

            # 设置表格固定表头，启用滚动
            grade_table.fixed_rows = 1
            grade_table.zebra_stripes = True

            # 添加数据
            for grade in grades:
                # 格式化成绩显示
                score_str = f"{grade.score:.1f}" if grade.score > 0 else "免修"
                grade_table.add_row(
                    grade.course_name,
                    score_str,
                    f"{grade.credit:.1f}",
                    grade.course_type,
                    grade.semester,
                )

            # 如果没有数据，显示提示
            if not grades:
                grade_table.add_row("暂无成绩数据", "", "", "", "")

        except Exception as e:
            # 显示错误信息
            grade_table = self.query_one("#grade_table", DataTable)
            grade_table.clear()
            if not grade_table.columns:
                grade_table.add_column("错误")
            grade_table.add_row(f"加载失败: {str(e)}")

    async def _load_courses(self) -> None:
        """加载课程表数据"""
        from ...api.course import CourseAPI

        try:
            course_api = CourseAPI(self.app.client)
            courses = await course_api.get_courses()

            # 获取课程表表格
            course_table = self.query_one("#course_table", DataTable)

            # 清空现有数据（保留列）
            course_table.clear()

            # 如果还没有列，添加列（时间表格式）
            if not course_table.columns:
                course_table.add_column("节次", key="period", width=10)
                course_table.add_column("周一", key="mon", width=20)
                course_table.add_column("周二", key="tue", width=20)
                course_table.add_column("周三", key="wed", width=20)
                course_table.add_column("周四", key="thu", width=20)
                course_table.add_column("周五", key="fri", width=20)
                course_table.add_column("周六", key="sat", width=20)
                course_table.add_column("周日", key="sun", width=20)

            # 设置表格固定表头，启用滚动
            course_table.fixed_rows = 1
            course_table.zebra_stripes = True

            # 构建时间表（第1-10节，每2节一行）
            time_slots = [
                ("第1-2节", 1, 2),
                ("第3-4节", 3, 4),
                ("第5-6节", 5, 6),
                ("第7-8节", 7, 8),
                ("第9-10节", 9, 10),
            ]

            for period_name, start, end in time_slots:
                row_data = [period_name]

                # 对于每一天（周一到周日），查找匹配的课程
                for day in range(1, 8):  # 1-7 代表周一到周日
                    day_courses = []
                    for course in courses:
                        # 检查课程是否在这一天，且时间有重叠
                        if (course.day == day and
                            not (course.end_node < start or course.start_node > end)):
                            # 有时间重叠，添加课程信息
                            course_info = f"{course.course_name}@{course.classroom}"
                            day_courses.append(course_info)

                    # 如果该时段有课程，显示课程；否则显示空
                    row_data.append("\n".join(day_courses) if day_courses else "")

                course_table.add_row(*row_data)

            # 如果没有数据，显示提示
            if not courses:
                course_table.add_row("暂无课程数据", "", "", "", "", "", "", "")

        except Exception as e:
            # 显示错误信息
            course_table = self.query_one("#course_table", DataTable)
            course_table.clear()
            if not course_table.columns:
                course_table.add_column("错误")
            course_table.add_row(f"加载失败: {str(e)}")

    async def _load_exams(self) -> None:
        """加载考试数据"""
        from ...api.exam import ExamAPI

        try:
            exam_api = ExamAPI(self.app.client)
            exams = await exam_api.get_exams()

            # 获取考试表格
            exam_table = self.query_one("#exam_table", DataTable)

            # 清空现有数据（保留列）
            exam_table.clear()

            # 如果还没有列，添加列
            if not exam_table.columns:
                exam_table.add_column("课程名称", key="course_name", width=25)
                exam_table.add_column("日期", key="exam_date", width=12)
                exam_table.add_column("时间", key="exam_time", width=12)
                exam_table.add_column("地点", key="classroom", width=20)
                exam_table.add_column("座位", key="seat_number", width=6)
                exam_table.add_column("考试形式", key="exam_type", width=12)
                exam_table.add_column("监考老师", key="teachers", width=20)

            # 设置表格固定表头，启用滚动
            exam_table.fixed_rows = 1
            exam_table.zebra_stripes = True

            # 添加数据
            for exam in exams:
                # 组合监考老师
                teachers = f"{exam.main_teacher}" if exam.main_teacher else ""
                if exam.assistant_teacher:
                    teachers += f"、{exam.assistant_teacher}" if teachers else exam.assistant_teacher

                exam_table.add_row(
                    exam.course_name,
                    exam.exam_date,
                    exam.exam_time,
                    exam.classroom,
                    exam.seat_number,
                    exam.exam_type,
                    teachers,
                )

            # 如果没有数据，显示提示
            if not exams:
                exam_table.add_row("暂无考试数据", "", "", "", "", "", "")

        except Exception as e:
            # 显示错误信息
            exam_table = self.query_one("#exam_table", DataTable)
            exam_table.clear()
            if not exam_table.columns:
                exam_table.add_column("错误")
            exam_table.add_row(f"加载失败: {str(e)}")

    async def _switch_mode(self, mode: str) -> None:
        """切换显示模式"""
        # 如果正在切换中，忽略此次请求
        if self._is_switching:
            return

        # 如果切换到当前模式，直接返回
        if self.current_mode == mode:
            return

        # 设置切换标志
        self._is_switching = True

        try:
            self.current_mode = mode

            # 获取内容区域
            content_area = self.query_one("#content_area", Vertical)

            # 清空容器并添加新表格
            content_area.remove_children()
            if mode == "grades":
                await content_area.mount(DataTable(id="grade_table"))
            elif mode == "courses":
                await content_area.mount(DataTable(id="course_table"))
            elif mode == "exams":
                await content_area.mount(DataTable(id="exam_table"))

            # 重新加载数据（在mount完成后再加载）
            if mode == "grades":
                await self._load_grades()
            elif mode == "courses":
                await self._load_courses()
            elif mode == "exams":
                await self._load_exams()

            # 更新按钮状态
            grades_btn = self.query_one("#grades_btn", Button)
            courses_btn = self.query_one("#courses_btn", Button)
            exams_btn = self.query_one("#exams_btn", Button)

            # 重置所有按钮
            grades_btn.variant = "default"
            courses_btn.variant = "default"
            exams_btn.variant = "default"

            # 设置当前按钮为primary
            if mode == "grades":
                grades_btn.variant = "primary"
            elif mode == "courses":
                courses_btn.variant = "primary"
            elif mode == "exams":
                exams_btn.variant = "primary"

        finally:
            # 无论成功或失败，都要重置切换标志
            self._is_switching = False

    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Header()
        yield Label("🎓 YJS 教务系统", id="dashboard_header")

        # 学生信息区域
        yield Vertical(id="student_info")

        # 主内容区域（左右布局）
        yield Horizontal(
            # 左侧边栏
            Vertical(
                Button("📚 成绩", id="grades_btn", variant="primary"),
                Button("📅 课程表", id="courses_btn", variant="default"),
                Button("✏️ 考试", id="exams_btn", variant="default"),
                id="sidebar",
            ),
            # 右侧内容区域
            Vertical(
                DataTable(id="grade_table"),
                id="content_area",
            ),
            id="main_content",
        )

        # 底部按钮区域
        yield Horizontal(
            Button("🔄 刷新", id="refresh_btn", variant="success"),
            Button("🚪 退出", id="logout_btn", variant="error"),
            id="bottom_actions",
        )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """按钮点击事件"""
        if event.button.id == "refresh_btn":
            # 刷新当前显示的数据
            if self.current_mode == "grades":
                self.run_worker(self._load_grades())
            elif self.current_mode == "courses":
                self.run_worker(self._load_courses())
            elif self.current_mode == "exams":
                self.run_worker(self._load_exams())
            self.app.notify("正在刷新数据...", severity="information")

        elif event.button.id == "logout_btn":
            # 退出登录并返回登录界面
            self.app.pop_screen()
            self.app.notify("已退出登录", severity="information")

        elif event.button.id == "grades_btn":
            # 切换到成绩视图
            self.run_worker(self._switch_mode("grades"))

        elif event.button.id == "courses_btn":
            # 切换到课程表视图
            self.run_worker(self._switch_mode("courses"))

        elif event.button.id == "exams_btn":
            # 切换到考试视图
            self.run_worker(self._switch_mode("exams"))