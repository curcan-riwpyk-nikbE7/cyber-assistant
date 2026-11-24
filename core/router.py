import os
import re
from tools.volume_control import VolumeController
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
from core.llm_engine import LLMEngine
from core.speaker import speaker

class CommandRouter:
    """Двухуровневый маршрутизатор команд (WinAPI / Громкость / Окна / LLM)."""
    
    def __init__(self, llm_engine: LLMEngine = None):
        self.llm = llm_engine if llm_engine else LLMEngine()
        self.volume = VolumeController()

    def route_command(self, text: str, speak: bool = True) -> dict:
        t = text.lower().strip()
        result = {}

        # -------------------------------------------------------------
        # 1. Управление громкостью (pycaw)
        # -------------------------------------------------------------
        if any(w in t for w in ["сделай громче", "прибавь громкость", "добавь громкость", "громче"]):
            match = re.search(r"\d+", t)
            step = int(match.group()) if match else 15
            res = self.volume.change_volume(step)
            result = {"action": "volume", "reply": res, "emotion": "happy"}

        elif any(w in t for w in ["сделай тише", "убавь громкость", "уменьши громкость", "тише"]):
            match = re.search(r"\d+", t)
            step = int(match.group()) if match else 15
            res = self.volume.change_volume(-step)
            result = {"action": "volume", "reply": res, "emotion": "happy"}

        elif any(w in t for w in ["заглуши", "выключи звук", "без звука", "мут", "mute"]):
            res = self.volume.set_mute(True)
            result = {"action": "volume", "reply": res, "emotion": "surprised"}

        elif any(w in t for w in ["включи звук", "верни звук", "размуть"]):
            res = self.volume.set_mute(False)
            result = {"action": "volume", "reply": res, "emotion": "happy"}

        elif any(w in t for w in ["громкость на максимум", "звук на максимум", "громкость 100"]):
            res = self.volume.set_volume(100)
            result = {"action": "volume", "reply": res, "emotion": "happy"}

        elif "громкость на" in t:
            match = re.search(r"\d+", t)
            if match:
                val = int(match.group())
                res = self.volume.set_volume(val)
                result = {"action": "volume", "reply": res, "emotion": "happy"}

        # -------------------------------------------------------------
        # 2. Управление окнами и рабочим столом (WinAPI)
        # -------------------------------------------------------------
        elif any(w in t for w in ["сверни всё", "сверни все", "свернуть все", "свернуть всё", "покажи рабочий стол", "на рабочий стол"]):
            toggle_show_desktop()
            result = {"action": "window", "reply": "Свернул все окна, сэр.", "emotion": "happy"}

        elif any(w in t for w in ["сверни окно", "свернуть окно", "сверни это окно", "сверни приложение"]):
            minimize_active_window()
            result = {"action": "window", "reply": "Окно свернуто.", "emotion": "happy"}

        elif any(w in t for w in ["разверни окно", "на весь экран", "разверни на максимум"]):
            maximize_active_window()
            result = {"action": "window", "reply": "Развернул на весь экран.", "emotion": "happy"}

        elif any(w in t for w in ["закрой окно", "закрой программу", "закрой приложение"]):
            close_active_window()
            result = {"action": "window", "reply": "Окно закрыто.", "emotion": "happy"}

        elif "переключи на" in t:
            target = t.replace("переключи на", "").strip()
            if target:
                ok = focus_window_by_title(target)
                if ok:
                    result = {"action": "window", "reply": f"Переключил на {target}.", "emotion": "happy"}
                else:
                    result = {"action": "window", "reply": f"Окно {target} не найдено, сэр.", "emotion": "guilty"}

        # -------------------------------------------------------------
        # 3. Браузер и Интернет
        # -------------------------------------------------------------
        elif any(w in t for w in ["найди на ютубе", "найди на youtube", "включи на ютубе", "найди в ютубе"]):
            query = re.sub(r".*(?:найди на ютубе|найди на youtube|включи на ютубе|найди в ютубе)", "", t).strip()
            if query:
                search_youtube(query)
                result = {"action": "browser", "reply": f"Ищу на YouTube: {query}.", "emotion": "happy"}

        elif any(w in t for w in ["найди в интернете", "найди в сети", "загугли", "поищи"]):
            query = re.sub(r".*(?:найди в интернете|найди в сети|загугли|поищи)", "", t).strip()
            if query:
                search_internet(query)
                result = {"action": "browser", "reply": f"Открыл поиск по запросу: {query}.", "emotion": "happy"}

        elif any(w in t for w in ["открой ютуб", "открой youtube"]):
            open_url("youtube.com")
            result = {"action": "browser", "reply": "YouTube открыт.", "emotion": "happy"}

        # -------------------------------------------------------------
        # 4. Запуск приложений и игр
        # -------------------------------------------------------------
        elif any(w in t for w in ["запусти", "открой", "включи"]) and "steam" in t:
            launch_app("steam")
            result = {"action": "app", "reply": "Steam запускается, сэр!", "emotion": "happy"}

        elif any(w in t for w in ["запусти", "открой", "включи"]) and ("браузер" in t or "хром" in t or "chrome" in t):
            launch_app("chrome")
            result = {"action": "app", "reply": "Браузер запущен.", "emotion": "happy"}

        elif any(w in t for w in ["запусти", "открой"]) and ("дискорд" in t or "discord" in t):
            launch_app("discord")
            result = {"action": "app", "reply": "Discord открыт.", "emotion": "happy"}

        elif any(w in t for w in ["запусти", "открой"]) and ("телеграм" in t or "telegram" in t):
            launch_app("telegram")
            result = {"action": "app", "reply": "Telegram открыт.", "emotion": "happy"}

        # -------------------------------------------------------------
        # 5. Мультимедиа
        # -------------------------------------------------------------
        elif any(w in t for w in ["пауза", "стоп", "продолжи", "плей"]) and ("музык" in t or "трек" in t or len(t.split()) <= 3):
            msg = toggle_play_pause()
            result = {"action": "media", "reply": msg, "emotion": "happy"}

        elif any(w in t for w in ["следующий трек", "следующая песня", "переключи трек"]):
            msg = next_track()
            result = {"action": "media", "reply": msg, "emotion": "happy"}

        # -------------------------------------------------------------
        # 6. Утренний брифинг и Сводка (Morning Briefing)
        # -------------------------------------------------------------
        elif any(w in t for w in ["утренний брифинг", "утренняя сводка", "утренний отчет", "сводка на день", "что на сегодня", "доброе утро", "брифинг"]):
            st = get_system_telemetry()
            import datetime
            now_str = datetime.datetime.now().strftime("%H:%M")
            reply_text = f"Доброе утро, сэр! На часах {now_str}. Процессор {st['cpu_percent']}%, свободно {st['disk_free_gb']} ГБ. Все системы ПК стабильны. Готов к выполнению задач!"
            result = {"action": "briefing", "reply": reply_text, "emotion": "happy"}

        # -------------------------------------------------------------
        # 7. Режимы работы (Сценарии и Макросы)
        # -------------------------------------------------------------
        elif any(w in t for w in ["режим работы", "режим разработчика", "рабочий режим"]):
            launch_app("chrome")
            result = {"action": "scenario", "reply": "Активирован рабочий режим, сэр! Браузер запущен, фокус настроен.", "emotion": "happy"}

        elif any(w in t for w in ["игровой режим", "режим игры"]):
            toggle_show_desktop()
            launch_app("steam")
            result = {"action": "scenario", "reply": "Игровой режим включен! Окна свернуты, Steam запускается.", "emotion": "happy"}

        # -------------------------------------------------------------
        # 8. Телеметрия железа
        # -------------------------------------------------------------
        elif any(w in t for w in ["нагрузка", "память", "диск", "температура", "статус системы", "как дела"]):
            st = get_system_telemetry()
            msg = f"Процессор {st['cpu_percent']}%, свободно {st['disk_free_gb']} ГБ на диске C. Все системы в норме!"
            result = {"action": "telemetry", "reply": msg, "emotion": "happy"}

        # -------------------------------------------------------------
        # 9. Интеллектуальный ответ через LLM (Ollama Local / Gemini)
        # -------------------------------------------------------------
        else:
            llm_res = self.llm.ask(text)
            result = {
                "action": "llm",
                "reply": llm_res.get("reply", "Слушаю вас, сэр."),
                "emotion": llm_res.get("emotion", "happy"),
                "provider": llm_res.get("provider", "LLM")
            }

        # Озвучиваем ответ через голосовой синтез DmitryNeural
        if speak and result.get("reply"):
            speaker.speak(result["reply"])

        return result
