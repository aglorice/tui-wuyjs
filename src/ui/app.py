"""TUI 主应用"""

import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from ..client.http_client import YJSClient
from .screens.course import CourseScreen
from .screens.dashboard import DashboardScreen
from .screens.grade import GradeScreen
from .screens.login import LoginScreen


class YJSApp(App):
    """YJS 教务系统 TUI 应用"""

    CSS = """
    #dashboard_container {
        align: center middle;
        width: 60;
        height: 15;
        border: thick $primary;
        padding: 2;
    }

    #menu_row {
        height: 3;
        align: center middle;
    }

    #menu_row Button {
        width: 16;
        margin: 0 1;
    }
    """

    TITLE = "YJS 教务系统"

    def __init__(self):
        super().__init__()
        self.client = YJSClient()

    def on_mount(self) -> None:
        """应用启动"""
        # 设置 Gruvbox 主题（使用环境变量）
        os.environ["TEXTUAL_THEME"] = "gruvbox_dark"
        # 推送登录界面
        self.push_screen(LoginScreen())

    def push_screen(self, screen: str | object) -> None:
        """
        推送屏幕到栈

        Args:
            screen: 屏幕名称或屏幕实例
        """
        if isinstance(screen, str):
            # 根据字符串名称推送屏幕
            if screen == "course":
                from .screens.course import CourseScreen
                super().push_screen(CourseScreen())
            elif screen == "grade":
                from .screens.grade import GradeScreen
                super().push_screen(GradeScreen())
            elif screen == "dashboard":
                from .screens.dashboard import DashboardScreen
                super().push_screen(DashboardScreen())
            else:
                super().push_screen(screen)
        else:
            super().push_screen(screen)