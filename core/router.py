import re
from tools.app_launcher import launch_app
from tools.media_control import toggle_play_pause, next_track, prev_track
from tools.telemetry import get_system_telemetry
from tools.window_manager import (
    minimize_active_window,
    maximize_active_window,
    close_active_window,
    toggle_show_desktop,
    focus_window_by_title
)
from tools.browser_tools import open_url, search_internet, search_youtube

class CommandRouter:
    """Двухуровневый маршрутизатор команд (WinAPI / Браузер / Окна / LLM)."""
    
    def __init__(self):
        pass

    def route_command(self, text: str) -> dict:
        t = text.lower().strip()

        # -------------------------------------------------------------
        # 1. Управление окнами и рабочим столом (WinAPI)
        # -------------------------------------------------------------
        if any(w in t for w in ["сверни всё", "сверни все", "покажи рабочий стол", "на рабочий стол"]):
            toggle_show_desktop()
            return {"action": "window", "reply": "Свернул все окна, сэр.", "emotion": "happy"}

        if any(w in t for w in ["сверни окно", "сверни это окно", "сверни приложение", "сверни программу"]):
            minimize_active_window()
            return {"action": "window", "reply": "Окно свернуто.", "emotion": "happy"}

        if any(w in t for w in ["разверни окно", "на весь экран", "разверни на максимум"]):
            maximize_active_window()
            return {"action": "window", "reply": "Развернул на весь экран.", "emotion": "happy"}

        if any(w in t for w in ["закрой окно", "закрой программу", "закрой приложение"]):
            close_active_window()
            return {"action": "window", "reply": "Окно закрыто.", "emotion": "happy"}

        if "переключи на" in t:
            target = t.replace("переключи на", "").strip()
            if target:
                ok = focus_window_by_title(target)
                if ok:
                    return {"action": "window", "reply": f"Переключил на {target}.", "emotion": "happy"}
                return {"action": "window", "reply": f"Окно {target} не найдено, сэр.", "emotion": "guilty"}

        # -------------------------------------------------------------
        # 2. Браузер и Интернет
        # -------------------------------------------------------------
        if any(w in t for w in ["найди на ютубе", "найди на youtube", "включи на ютубе", "найди в ютубе"]):
            query = re.sub(r".*(?:найди на ютубе|найди на youtube|включи на ютубе|найди в ютубе)", "", t).strip()
            if query:
                search_youtube(query)
                return {"action": "browser", "reply": f"Ищу на YouTube: «{query}».", "emotion": "happy"}

        if any(w in t for w in ["найди в интернете", "найди в сети", "загугли", "поищи"]):
            query = re.sub(r".*(?:найди в интернете|найди в сети|загугли|поищи)", "", t).strip()
            if query:
                search_internet(query)
                return {"action": "browser", "reply": f"Открыл поиск по запросу: «{query}».", "emotion": "happy"}

        if any(w in t for w in ["открой ютуб", "открой youtube"]):
            open_url("youtube.com")
            return {"action": "browser", "reply": "YouTube открыт.", "emotion": "happy"}

        # -------------------------------------------------------------
        # 3. Запуск приложений
        # -------------------------------------------------------------
        if any(w in t for w in ["запусти", "открой", "включи"]) and "steam" in t:
            ok = launch_app("steam")
            return {"action": "app", "reply": "Steam запускается, сэр!", "emotion": "happy"}

        if any(w in t for w in ["запусти", "открой", "включи"]) and ("браузер" in t or "хром" in t or "chrome" in t):
            ok = launch_app("chrome")
            return {"action": "app", "reply": "Браузер запущен.", "emotion": "happy"}

        if any(w in t for w in ["запусти", "открой"]) and ("дискорд" in t or "discord" in t):
            ok = launch_app("discord")
            return {"action": "app", "reply": "Discord открыт.", "emotion": "happy"}

        if any(w in t for w in ["запусти", "открой"]) and ("телеграм" in t or "telegram" in t):
            ok = launch_app("telegram")
            return {"action": "app", "reply": "Telegram открыт.", "emotion": "happy"}

        # -------------------------------------------------------------
        # 4. Мультимедиа
        # -------------------------------------------------------------
        if any(w in t for w in ["пауза", "стоп", "продолжи", "плей"]) and ("музык" in t or "трек" in t or len(t.split()) <= 3):
            msg = toggle_play_pause()
            return {"action": "media", "reply": msg, "emotion": "happy"}

        if any(w in t for w in ["следующий трек", "следующая песня", "переключи трек"]):
            msg = next_track()
            return {"action": "media", "reply": msg, "emotion": "happy"}

        # -------------------------------------------------------------
        # 5. Телеметрия железа
        # -------------------------------------------------------------
        if any(w in t for w in ["нагрузка", "память", "диск", "температура", "статус системы", "как дела"]):
            st = get_system_telemetry()
            msg = f"Процессор {st['cpu_percent']}%, свободно {st['disk_free_gb']} ГБ на диске C. Все системы в норме!"
            return {"action": "telemetry", "reply": msg, "emotion": "happy"}

        # -------------------------------------------------------------
        # 6. Ответ при отсутствии прямого системного шаблона
        # -------------------------------------------------------------
        return {
            "action": "llm",
            "reply": "Ну... почти, сэр. Отправляю запрос в нейросеть.",
            "emotion": "guilty"
        }
