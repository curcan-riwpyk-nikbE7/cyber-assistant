import os
import sys
import webview
import threading
from core.router import CommandRouter
from core.updater import AppUpdater
from tools.telemetry import get_system_telemetry

class DesktopBridge:
    """Двусторонний API-мост между JavaScript интерфейсом и Python бэкендом."""
    def __init__(self, window_ref=None, repo_dir=None):
        self.router = CommandRouter()
        self.window = window_ref
        self.repo_dir = repo_dir or os.path.dirname(__file__)
        self.updater = AppUpdater(self.repo_dir)

    def set_window(self, window):
        self.window = window

    def execute_command(self, text: str) -> dict:
        """Принимает команду из интерфейса и запускает выполнение в Windows."""
        return self.router.route_command(text)

    def get_telemetry(self) -> dict:
        """Отдает актуальную сводку процессора, видеокарты и диска."""
        return get_system_telemetry()

    def check_updates(self) -> dict:
        """Проверяет обновления через GitHub репозиторий."""
        return self.updater.check_for_updates()

    def perform_update(self) -> dict:
        """Скачивает и накатывает обновления из GitHub."""
        return self.updater.apply_update()

    # Оконные системные кнопки (Кастомный Frameless заголовок окна)
    def window_minimize(self):
        if self.window:
            self.window.minimize()

    def window_toggle_maximize(self):
        if self.window:
            # webview maximize/restore
            pass

    def window_close(self):
        if self.window:
            self.window.destroy()

def start_desktop_app():
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")
    if not os.path.exists(ui_path):
        print(f"Error: UI file not found at {ui_path}")
        return

    bridge = DesktopBridge()

    # Создаем нативное окно с кастомным безрамочным стилем (frameless=True)
    window = webview.create_window(
        title="CYBER Assistant // KINGSAID EDITION",
        url=f"file:///{ui_path}",
        width=1160,
        height=760,
        frameless=True,
        easy_drag=True,
        resizable=True,
        min_size=(960, 640),
        js_api=bridge,
        background_color="#06080d"
    )
    bridge.set_window(window)

    webview.start(debug=False)

if __name__ == "__main__":
    start_desktop_app()
