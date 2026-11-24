import os
import time
import threading
import speech_recognition as sr
from core.speaker import speaker

class VoiceListener:
    """Непрерывный фоновый слушатель микрофона (активация по фразе «Кибер»)."""

    def __init__(self, router=None, trigger_word="кибер"):
        self.router = router
        self.trigger_word = trigger_word.lower()
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[VoiceListener] Фоновый голосовой контур запущен (триггер: «{self.trigger_word}»).")

    def _loop(self):
        # Инициализируем микрофон
        try:
            mic = sr.Microphone()
        except Exception as e:
            print(f"[VoiceListener] Микрофон недоступен: {e}")
            return

        while self._running:
            try:
                with mic as source:
                    # Слушаем аудиопоток
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=7)
                
                # Распознаем через быстрый Google STT API (русский язык)
                try:
                    text = self.recognizer.recognize_google(audio, language="ru-RU").lower().strip()
                    print(f"[VoiceListener] Услышано: «{text}»")

                    # Проверяем триггерное слово «Кибер»
                    if self.trigger_word in text:
                        # Убираем имя ассистента из команды
                        cmd = text.replace(self.trigger_word, "").strip()
                        if not cmd:
                            speaker.speak("Слушаю вас, сэр.")
                        else:
                            if self.router:
                                self.router.route_command(cmd, speak=True)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"[VoiceListener] Ошибка сервиса распознавания: {e}")
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                time.sleep(1)
