import os
import sys
import webview
import threading
from core.router import CommandRouter
from tools.telemetry import get_system_telemetry

class DesktopBridge:
    """Двусторонний API-мост между JavaScript интерфейсом и Python бэкендом."""
    def __init__(self, window_ref=None):
        self.router = CommandRouter()
        self.window = window_ref

    def set_window(self, window):
        self.window = window

    def execute_command(self, text: str) -> dict:
        """Принимает команду из интерфейса и запускает выполнение в Windows."""
        res = self.router.route_command(text)
        return res

    def get_telemetry(self) -> dict:
        """Отдает актуальную сводку процессора, видеокарты и диска."""
        return get_system_telemetry()

def start_desktop_app():
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")
    if not os.path.exists(ui_path):
        print(f"Error: UI file not found at {ui_path}")
        return

    bridge = DesktopBridge()

    # Создаем нативное десктопное окно Windows (Edge WebView2)
    window = webview.create_window(
        title="CYBER Assistant // KINGSAID EDITION",
        url=f"file:///{ui_path}",
        width=1120,
        height=740,
        resizable=True,
        min_size=(900, 600),
        js_api=bridge,
        background_color="#06080d"
    )
    bridge.set_window(window)

    # Запуск цикла оконного приложения
    webview.start(debug=False)

if __name__ == "__main__":
    start_desktop_app()
