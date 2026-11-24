import os
import sys
import json
import time
import subprocess
import http.server
import socketserver
from urllib.parse import urlparse

from core.router import CommandRouter
from core.updater import AppUpdater
from core.plugins import PluginManager
from tools.telemetry import get_system_telemetry

PORT = 54321
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")
router = CommandRouter()
updater = AppUpdater(os.path.dirname(__file__))
plugin_manager = PluginManager()

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
                response_data = router.route_command(cmd)
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

def launch_chrome_or_edge():
    app_url = f"http://127.0.0.1:{PORT}/index.html"
    user_data = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CyberAppProfile")

    # Ищем Chrome или Edge
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
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", PORT), AppHandler)
    
    # Запускаем окно приложения через 0.5 сек после старта сокета
    import threading
    threading.Timer(0.5, launch_chrome_or_edge).start()

    print(f"Cyber Assistant backend running on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    main()
