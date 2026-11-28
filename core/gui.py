import os
import sys
import subprocess
import webbrowser

def run_native_window(url: str, title: str = "Кибер — Твой персональный ИИ", width: int = 1180, height: int = 780):
    """
    Запускает нативное, безрамочное приложение через Edge PWA или Chrome App mode.
    Полностью обходит блокировку Smart App Control (DLL lock) Windows.
    """
    browsers = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    target = next((b for b in browsers if os.path.exists(b)), None)
    profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CyberAppRuntime")

    if target:
        cmd = [
            target,
            f"--app={url}",
            f"--user-data-dir={profile_dir}",
            f"--window-size={width},{height}",
            "--window-position=180,100"
        ]
        try:
            p = subprocess.Popen(cmd)
            print(f"[WindowRuntime] Окно запущено через {os.path.basename(target)} (PID: {p.pid})")
            p.wait()
            return
        except Exception as e:
            print(f"[WindowRuntime] Ошибка запуска браузера: {e}")

    # Фолбэк на системный браузер
    webbrowser.open(url)
