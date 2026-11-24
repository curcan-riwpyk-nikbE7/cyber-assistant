import os
import sys
import json
from PyQt6.QtCore import QUrl, pyqtSlot, QObject, Qt, QPoint
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from core.router import CommandRouter
from core.updater import AppUpdater
from tools.telemetry import get_system_telemetry

class WebBridge(QObject):
    """Мост связи между JavaScript в интерфейсе и Python."""
    def __init__(self, main_window):
        super().__init__()
        self.win = main_window
        self.router = CommandRouter()
        self.updater = AppUpdater(os.path.dirname(__file__))

    @pyqtSlot(str, result=str)
    def executeCommand(self, cmd_text):
        res = self.router.route_command(cmd_text)
        return json.dumps(res)

    @pyqtSlot(result=str)
    def getTelemetry(self):
        return json.dumps(get_system_telemetry())

    @pyqtSlot(result=str)
    def checkUpdates(self):
        return json.dumps(self.updater.check_for_updates())

    @pyqtSlot(result=str)
    def performUpdate(self):
        return json.dumps(self.updater.apply_update())

    @pyqtSlot()
    def minimizeWindow(self):
        self.win.showMinimized()

    @pyqtSlot()
    def toggleMaximizeWindow(self):
        if self.win.isMaximized():
            self.win.showNormal()
        else:
            self.win.showMaximized()

    @pyqtSlot()
    def closeWindow(self):
        self.win.close()


class CyberMainWindow(QMainWindow):
    """Главное нативное окно приложения Кибер на движке Qt6 WebEngine."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Assistant // KINGSAID OS")
        self.resize(1160, 760)
        self.setMinimumSize(960, 640)

        # Делаем окно безрамочным (Frameless) как в Discord / Astra
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Веб-движок Chromium
        self.browser = QWebEngineView()
        self.browser.page().setBackgroundColor(Qt.GlobalColor.transparent)

        # Канал связи
        self.channel = QWebChannel()
        self.bridge = WebBridge(self)
        self.channel.registerObject("pyBridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        # Загрузка локального UI
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")
        self.browser.load(QUrl.fromLocalFile(os.path.abspath(ui_path)))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Поддержка плавного перетаскивания окна мышь
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 50:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and event.pos().y() < 50:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def run_app():
    # Отключаем лишнее черное окно консоли
    app = QApplication(sys.argv)
    window = CyberMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
