import ctypes
import time

user32 = ctypes.windll.user32

# Windows Constants
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
WM_CLOSE = 0x0010

VK_LWIN = 0x5B
VK_D = 0x44
KEYEVENTF_KEYUP = 0x0002

def get_active_window():
    """Возвращает дескриптор (hwnd) и заголовок активного окна."""
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return hwnd, buff.value

def minimize_active_window() -> bool:
    """Сворачивает текущее активное окно."""
    hwnd, title = get_active_window()
    if hwnd:
        user32.ShowWindow(hwnd, SW_MINIMIZE)
        return True
    return False

def maximize_active_window() -> bool:
    """Разворачивает активное окно на весь экран."""
    hwnd, title = get_active_window()
    if hwnd:
        user32.ShowWindow(hwnd, SW_MAXIMIZE)
        return True
    return False

def close_active_window() -> bool:
    """Закрывает текущее активное окно."""
    hwnd, title = get_active_window()
    if hwnd:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return True
    return False

def toggle_show_desktop() -> bool:
    """Сворачивает ВСЕ окна и показывает рабочий стол (Win + D)."""
    user32.keybd_event(VK_LWIN, 0, 0, 0)
    user32.keybd_event(VK_D, 0, 0, 0)
    user32.keybd_event(VK_D, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
    return True

def focus_window_by_title(keyword: str) -> bool:
    """Ищет окно по ключевому слову в заголовке и выводит на передний план."""
    keyword = keyword.lower()
    found_hwnd = None

    def enum_windows_callback(hwnd, extra):
        nonlocal found_hwnd
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if keyword in buff.value.lower():
                    found_hwnd = hwnd
                    return False  # stop enumeration
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

    if found_hwnd:
        user32.ShowWindow(found_hwnd, SW_RESTORE)
        user32.SetForegroundWindow(found_hwnd)
        return True
    return False

if __name__ == "__main__":
    hwnd, title = get_active_window()
    print(f"Active window: hwnd={hwnd}, title='{title}'")
