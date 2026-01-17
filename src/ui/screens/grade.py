"""成绩界面"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Header, Footer


class GradeScreen(Screen):
    """成绩界面"""

    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Header()
        yield DataTable(id="grade_table")
        yield Footer()

    def on_mount(self) -> None:
        """界面挂载"""
        table = self.query_one(DataTable)
        table.add_columns("课程名称", "成绩", "学分", "绩点", "学期")

    async def load_grades(self, grades: list):
        """加载成绩数据"""
        table = self.query_one(DataTable)
        table.clear()

        for grade in grades:
            table.add_row(
                grade.course_name,
                str(grade.score),
                str(grade.credit),
                str(grade.gpa),
                grade.semester,
            )