"""登录界面"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Center
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Footer, Checkbox


class LoginScreen(Screen):
    """登录界面"""

    CSS = """
    Screen {
        layout: vertical;
    }

    #login_wrapper {
        height: 100%;
        align: center middle;
    }

    #login_container {
        width: 60;
        border: thick $primary;
        padding: 3;
        background: $panel;
    }

    #title {
        text-align: center;
        text-style: bold;
        padding: 1;
        margin-bottom: 2;
        color: $primary;
    }

    .label {
        padding: 1 0;
    }

    Input {
        margin: 0 0 1 0;
        width: 100%;
    }

    #remember_row {
        margin: 1 0;
    }

    #button_row {
        margin-top: 2;
        align: center middle;
    }

    Button {
        width: 16;
        margin: 0 1;
    }
    """

    def on_mount(self) -> None:
        """界面加载时自动填充保存的凭据"""
        from ...storage.state import credentials_manager

        # 尝试加载保存的凭据
        credentials = credentials_manager.load_credentials()
        if credentials:
            user_id, password = credentials
            user_id_input = self.query_one("#user_id", Input)
            password_input = self.query_one("#password", Input)
            remember_checkbox = self.query_one("#remember", Checkbox)

            user_id_input.value = user_id
            password_input.value = password
            remember_checkbox.value = True

    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Header()
        yield Center(
            Vertical(
                Label("YJS 教务系统", id="title"),
                Label("学号:", classes="label"),
                Input(placeholder="请输入学号", id="user_id"),
                Label("密码:", classes="label"),
                Input(placeholder="请输入密码", id="password", password=True),
                Horizontal(
                    Checkbox("记住密码", id="remember", value=False),
                    id="remember_row",
                ),
                Horizontal(
                    Button("登录", id="login_btn", variant="primary"),
                    Button("退出", id="exit_btn", variant="default"),
                    id="button_row",
                ),
                id="login_container",
            ),
            id="login_wrapper",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """按钮点击事件"""
        if event.button.id == "login_btn":
            self._login()
        elif event.button.id == "exit_btn":
            self.app.exit()

    def _login(self) -> None:
        """登录"""
        # 获取Input组件的值
        user_id_input = self.query_one("#user_id", Input)
        password_input = self.query_one("#password", Input)
        remember_checkbox = self.query_one("#remember", Checkbox)

        user_id = user_id_input.value.strip()
        password = password_input.value.strip()
        remember = remember_checkbox.value

        if not user_id or not password:
            self.app.notify("请输入学号和密码", severity="error")
            return

        # 调用异步登录逻辑
        self.run_worker(self._perform_login(user_id, password, remember), exclusive=True)

    async def _perform_login(self, user_id: str, password: str, remember: bool = False) -> None:
        """
        执行登录流程

        Args:
            user_id: 学号
            password: 密码
            remember: 是否记住密码
        """
        from ...auth.login import LoginManager
        from .dashboard import DashboardScreen
        from ...storage.state import credentials_manager

        # 禁用登录按钮
        login_btn = self.query_one("#login_btn", Button)
        login_btn.disabled = True
        login_btn.label = "登录中..."

        try:
            # 初始化客户端
            await self.app.client.initialize()

            # 执行登录（带进度提示）
            login_manager = LoginManager(self.app.client)
            self.app.notify("正在识别验证码...", severity="information")

            # 使用回调函数接收登录进度
            def progress_callback(message: str, severity: str = "information"):
                self.app.notify(message, severity=severity)

            result = await login_manager.login(user_id, password, progress_callback=progress_callback)

            # 验证登录状态
            if not self.app.client.is_logged_in:
                raise Exception("登录状态未设置，请重试")

            # 登录成功，保存凭据（如果勾选了记住密码）
            if remember:
                credentials_manager.save_credentials(user_id, password)
                self.app.notify("登录成功！已保存账号密码", severity="information")
            else:
                # 如果没有勾选记住密码，清除之前保存的凭据
                credentials_manager.clear_credentials()
                self.app.notify("登录成功！", severity="information")

            # 清空输入框
            user_id_input = self.query_one("#user_id", Input)
            password_input = self.query_one("#password", Input)
            user_id_input.value = ""
            password_input.value = ""

            # 跳转到仪表盘（不需要 await）
            self.app.push_screen(DashboardScreen())

        except Exception as e:
            self.app.notify(f"登录失败: {str(e)}", severity="error")
        finally:
            # 恢复登录按钮
            login_btn.disabled = False
            login_btn.label = "登录"