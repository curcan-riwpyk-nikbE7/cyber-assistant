import os
import subprocess
import shutil

KNOWN_APPS = {
    "steam": [
        r"C:\Program Files (x86)\Steam\steam.exe",
        r"C:\Program Files\Steam\steam.exe"
    ],
    "discord": [
        os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe")
    ],
    "telegram": [
        os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe")
    ],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ],
    "browser": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ],
    "terminal": "cmd.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe"
}

def launch_app(app_name: str) -> bool:
    """Запускает программу по её псевдониму или прямому пути."""
    app_key = app_name.lower().strip()
    
    if app_key in KNOWN_APPS:
        paths = KNOWN_APPS[app_key]
        if isinstance(paths, str):
            subprocess.Popen(paths, shell=True)
            return True
        for p in paths:
            clean_path = p.split()[0]
            if os.path.exists(clean_path):
                subprocess.Popen(p, shell=True)
                return True
    
    # Try finding executable in PATH
    which_path = shutil.which(app_key)
    if which_path:
        subprocess.Popen(which_path, shell=True)
        return True

    return False
