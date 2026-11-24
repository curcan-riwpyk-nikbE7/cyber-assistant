import os
import threading
import keyboard
import win32gui
import win32con

class HotkeyManager:
    """Глобальный обработчик горячих клавиш (Alt + Space)."""

    def __init__(self, hotkey: str = "alt+space", callback=None):
        self.hotkey = hotkey
        self.callback = callback
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        try:
            keyboard.add_hotkey(self.hotkey, self._on_triggered)
            print(f"[HotkeyManager] Хоткей «{self.hotkey}» успешно зарегистрирован.")
        except Exception as e:
            print(f"[HotkeyManager] Ошибка регистрации хоткея: {e}")

    def _on_triggered(self):
        print(f"[HotkeyManager] Сработал хоткей {self.hotkey}!")
        self.bring_window_to_front()
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                print(f"[HotkeyManager] Ошибка в callback: {e}")

    def bring_window_to_front(self):
        """Находит окно Cyber Assistant и выводит его на передний план."""
        def enum_windows_callback(hwnd, extra):
            title = win32gui.GetWindowText(hwnd)
            if "Cyber Assistant" in title or "CYBER ASSISTANT" in title:
                extra.append(hwnd)

        hwnds = []
        win32gui.EnumWindows(enum_windows_callback, hwnds)
        if hwnds:
            target_hwnd = hwnds[0]
            try:
                win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(target_hwnd)
            except Exception as e:
                print(f"[HotkeyManager] Не удалось сфокусировать окно: {e}")
