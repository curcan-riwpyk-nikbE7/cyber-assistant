import os
import threading
import pystray
from PIL import Image

class SystemTrayManager:
    """Управление системным треем Windows (значок возле часов)."""

    def __init__(self, on_open=None, on_exit=None):
        self.on_open = on_open
        self.on_exit = on_exit
        self.icon = None
        self._thread = None

    def start(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.png")
        if not os.path.exists(icon_path):
            image = Image.new('RGB', (64, 64), color=(6, 182, 212))
        else:
            image = Image.open(icon_path)

        menu = pystray.Menu(
            pystray.MenuItem("Открыть Кибера (Alt+Space)", self._on_open_clicked, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", self._on_exit_clicked)
        )

        self.icon = pystray.Icon("CyberAssistant", image, "Кибер — Твой персональный ИИ", menu)
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()
        print("[SystemTray] Иконка в системном трее активна.")

    def _on_open_clicked(self, icon, item):
        if self.on_open:
            self.on_open()

    def _on_exit_clicked(self, icon, item):
        icon.stop()
        if self.on_exit:
            self.on_exit()
        else:
            os._exit(0)
