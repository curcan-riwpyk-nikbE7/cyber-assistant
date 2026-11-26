import os
import sys
import json
import time
import subprocess
import threading
import http.server
import socketserver
from urllib.parse import urlparse

from core.router import CommandRouter
from core.updater import AppUpdater
from core.plugins import PluginManager
from core.llm_engine import LLMEngine
from core.speaker import speaker
from core.hotkey import HotkeyManager
from core.listener import VoiceListener
from core.telegram_companion import TelegramCompanion
from core.tray import SystemTrayManager
from tools.telemetry import get_system_telemetry

PORT = 54321
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")
llm_engine = LLMEngine(provider="ollama", model="qwen2.5:3b")
router = CommandRouter(llm_engine=llm_engine)
updater = AppUpdater(os.path.dirname(__file__))
plugin_manager = PluginManager()

# Фоновые демоны
hotkey_manager = HotkeyManager(hotkey="alt+space")
voice_listener = VoiceListener(router=router, trigger_word="кибер")
telegram_companion = TelegramCompanion(router=router)

class AppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        response_data = {}

        if parsed.path == "/api/execute":
            try:
                body = json.loads(post_data)
                cmd = body.get("command", "")
                response_data = router.route_command(cmd, speak=True)
            except Exception as e:
                response_data = {"reply": f"Ошибка: {e}", "emotion": "guilty", "action": "error"}

        elif parsed.path == "/api/telemetry":
            response_data = get_system_telemetry()

        elif parsed.path == "/api/plugins":
            response_data = plugin_manager.get_plugins_list()

        elif parsed.path == "/api/toggle_plugin":
            try:
                body = json.loads(post_data)
                pid = body.get("plugin_id", "")
                response_data = plugin_manager.toggle_plugin(pid)
            except Exception as e:
                response_data = {"success": False, "error": str(e)}

        elif parsed.path == "/api/check_updates":
            response_data = updater.check_for_updates()

        elif parsed.path == "/api/perform_update":
            response_data = updater.apply_update()

        elif parsed.path == "/api/get_llm_config":
            response_data = {
                "provider": llm_engine.provider,
                "model": llm_engine.model,
                "gemini_key_set": bool(llm_engine.gemini_key)
            }

        elif parsed.path == "/api/set_llm_config":
            try:
                body = json.loads(post_data)
                provider = body.get("provider", "ollama")
                model = body.get("model", "qwen2.5:3b")
                gemini_key = body.get("gemini_key")
                llm_engine.set_provider(provider, model, gemini_key)
                response_data = {
                    "success": True,
                    "provider": llm_engine.provider,
                    "model": llm_engine.model
                }
            except Exception as e:
                response_data = {"success": False, "error": str(e)}

        elif parsed.path == "/api/toggle_speech":
            try:
                body = json.loads(post_data)
                speaker.enabled = body.get("enabled", True)
                response_data = {"success": True, "enabled": speaker.enabled}
            except Exception as e:
                response_data = {"success": False, "error": str(e)}

        elif parsed.path == "/api/start_telegram":
            try:
                body = json.loads(post_data)
                token = body.get("token", "")
                telegram_companion.start(token)
                response_data = {"success": True}
            except Exception as e:
                response_data = {"success": False, "error": str(e)}

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass

def ensure_ollama_running():
    """Проверяет, запущен ли Ollama daemon, и при необходимости стартует его в фоне."""
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1)
        print("[Ollama] Демон уже активен.")
    except Exception:
        print("[Ollama] Запуск локального демона нейросети...")
        ollama_bin = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
        if os.path.exists(ollama_bin):
            subprocess.Popen([ollama_bin, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)

def launch_chrome_or_edge():
    app_url = f"http://127.0.0.1:{PORT}/index.html"
    user_data = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CyberAppProfile")

    browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    target_browser = next((b for b in browsers if os.path.exists(b)), None)

    if target_browser:
        cmd = [
            target_browser,
            f"--app={app_url}",
            f"--user-data-dir={user_data}",
            "--window-size=1180,780",
            "--window-position=200,100"
        ]
        subprocess.Popen(cmd)
    else:
        import webbrowser
        webbrowser.open(app_url)

def main():
    # 1. Автозапуск Ollama при старте
    ensure_ollama_running()

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", PORT), AppHandler)
    
    # 2. Запуск окна интерфейса
    threading.Timer(0.5, launch_chrome_or_edge).start()

    # 3. Запуск глобального вызова Alt + Space
    try:
        hotkey_manager.start()
    except Exception as e:
        print(f"Ошибка хоткея: {e}")

    # 4. Фоновый голосовой слушатель микрофона
    try:
        voice_listener.start()
    except Exception as e:
        print(f"Ошибка слушателя микрофона: {e}")

    # 5. Иконка в системном трее Windows
    try:
        tray = SystemTrayManager(
            on_open=hotkey_manager.bring_window_to_front,
            on_exit=lambda: os._exit(0)
        )
        tray.start()
    except Exception as e:
        print(f"Ошибка трея: {e}")

    print(f"Cyber Assistant running on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    main()
