import os
import subprocess
import urllib.request
import json

REPO_API_URL = "https://api.github.com/repos/curcan-riwpyk-nikbE7/cyber-assistant"

class AppUpdater:
    """Модуль автообновления приложения Cyber Assistant через GitHub."""

    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir

    def check_for_updates(self) -> dict:
        """Проверяет наличие свежих коммитов в удаленной ветке GitHub."""
        try:
            # Стягиваем информацию о коммитах с удаленного репозитория
            subprocess.run(["git", "fetch", "origin", "main"], cwd=self.repo_dir, capture_output=True, text=True, check=True)
            
            # Сравниваем локальный HEAD и origin/main
            local_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo_dir, capture_output=True, text=True).stdout.strip()
            remote_commit = subprocess.run(["git", "rev-parse", "origin/main"], cwd=self.repo_dir, capture_output=True, text=True).stdout.strip()

            if local_commit != remote_commit:
                # Получаем последнее сообщение коммита
                msg = subprocess.run(["git", "log", "-1", "--pretty=%B", "origin/main"], cwd=self.repo_dir, capture_output=True, text=True).stdout.strip()
                return {
                    "has_update": True,
                    "latest_commit": remote_commit[:7],
                    "message": msg
                }
            return {
                "has_update": False,
                "latest_commit": local_commit[:7],
                "message": "У вас установлена последняя версия."
            }
        except Exception as e:
            return {"has_update": False, "error": str(e), "message": "Не удалось проверить обновления."}

    def apply_update(self) -> dict:
        """Скачивает и накатывает свежий код из GitHub (git pull)."""
        try:
            res = subprocess.run(["git", "pull", "origin", "main"], cwd=self.repo_dir, capture_output=True, text=True, check=True)
            return {"success": True, "output": res.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    updater = AppUpdater(os.path.dirname(os.path.dirname(__file__)))
    print("Update check:", updater.check_for_updates())
