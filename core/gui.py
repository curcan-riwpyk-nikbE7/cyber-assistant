import os
import sys
import threading

def run_native_qt_window(url: str, title: str = "Кибер — Твой персональный ИИ", width: int = 1180, height: int = 780):
    """Запускает нативное окно на движке Qt6 WebEngine (полноценный Chromium без зависимостей от внешних браузеров)."""
    try:
        from PyQt6.QtCore import QUrl
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWebEngineWidgets import QWebEngineView

        # Инициализируем Qt приложение
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        app.setApplicationName("CyberAssistant")

        view = QWebEngineView()
        view.setWindowTitle(title)
        view.resize(width, height)

        # Ставим кастомную иконку окна
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.png")
        if os.path.exists(icon_path):
            view.setWindowIcon(QIcon(icon_path))

        view.load(QUrl(url))
        view.show()
        print("[NativeGUI] Окно Qt6 WebEngine успешно открыто.")
        app.exec()
    except Exception as e:
        print(f"[NativeGUI] Ошибка Qt: {e}. Запуск системного браузера...")
        import webbrowser
        webbrowser.open(url)
