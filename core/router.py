import re
from tools.app_launcher import launch_app
from tools.media_control import toggle_play_pause, next_track, prev_track
from tools.telemetry import get_system_telemetry

class CommandRouter:
    """Быстрый контур обработки системных команд (отклик 5-15 мс)."""
    
    def __init__(self):
        pass

    def route_command(self, text: str) -> dict:
        t = text.lower().strip()
        
        # 1. Запуск программ
        if any(w in t for w in ["запусти", "открой", "включи"]) and "steam" in t:
            ok = launch_app("steam")
            return {"action": "app", "success": ok, "reply": "Steam запускается, сэр!", "emotion": "happy"}

        if any(w in t for w in ["запусти", "открой", "включи"]) and ("браузер" in t or "хром" in t or "chrome" in t):
            ok = launch_app("chrome")
            return {"action": "app", "success": ok, "reply": "Браузер открыт.", "emotion": "happy"}

        if any(w in t for w in ["запусти", "открой"]) and ("дискорд" in t or "discord" in t):
            ok = launch_app("discord")
            return {"action": "app", "success": ok, "reply": "Discord запущен.", "emotion": "happy"}

        if any(w in t for w in ["запусти", "открой"]) and ("телеграм" in t or "telegram" in t):
            ok = launch_app("telegram")
            return {"action": "app", "success": ok, "reply": "Telegram открыт.", "emotion": "happy"}

        # 2. Управление медиа
        if any(w in t for w in ["пауза", "стоп", "продолжи", "плей"]) and ("музык" in t or "трек" in t or len(t.split()) <= 3):
            msg = toggle_play_pause()
            return {"action": "media", "success": True, "reply": msg, "emotion": "happy"}

        if "следующий трек" in t or "следующая песня" in t or "переключи трек" in t:
            msg = next_track()
            return {"action": "media", "success": True, "reply": msg, "emotion": "happy"}

        # 3. Системный статус / Телеметрия
        if any(w in t for w in ["нагрузка", "память", "диск", "температура", "статус системы", "как дела"]):
            st = get_system_telemetry()
            msg = f"Процессор загружен на {st['cpu_percent']}%, свободно {st['disk_free_gb']} ГБ на диске C. Все системы в норме!"
            return {"action": "telemetry", "success": True, "reply": msg, "emotion": "happy"}

        # Если прямого соответствия нет - передаем в LLM
        return {
            "action": "llm",
            "success": False,
            "reply": "Ну... почти, сэр. Отправляю запрос в нейросеть.",
            "emotion": "guilty"
        }
