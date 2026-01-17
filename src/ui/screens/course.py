"""课程表界面"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Header, Footer


class CourseScreen(Screen):
    """课程表界面"""

    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Header()
        yield DataTable(id="course_table")
        yield Footer()

    def on_mount(self) -> None:
        """界面挂载"""
        table = self.query_one(DataTable)
        table.add_columns("节次", "周一", "周二", "周三", "周四", "周五", "周六", "周日")

        # 添加示例数据
        for i in range(1, 13):
            table.add_row(f"{i}-{i+1}", "", "", "", "", "", "", "")

    async def load_courses(self, courses: list):
        """加载课程数据"""
        table = self.query_one(DataTable)
        # TODO: 根据课程数据填充表格
        pass