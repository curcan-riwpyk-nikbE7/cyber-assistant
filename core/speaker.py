import os
import time
import asyncio
import tempfile
import threading
import edge_tts
import pygame

class Speaker:
    """Модуль озвучивания ответов в реальном времени (DmitryNeural / edge-tts)."""

    def __init__(self, voice: str = "ru-RU-DmitryNeural"):
        self.voice = voice
        self.enabled = True
        self.lock = threading.Lock()
        self._pygame_inited = False

    def _ensure_mixer(self):
        if not self._pygame_inited:
            try:
                pygame.mixer.init()
                self._pygame_inited = True
            except Exception as e:
                print(f"[Speaker] Ошибка инициализации звуковой подсистемы: {e}")

    def speak(self, text: str):
        """Озвучивает текст в отдельном неблокирующем потоке."""
        if not self.enabled or not text or not text.strip():
            return

        clean_text = self._sanitize_text(text)
        if not clean_text:
            return

        thread = threading.Thread(target=self._synthesize_and_play, args=(clean_text,), daemon=True)
        thread.start()

    def _sanitize_text(self, text: str) -> str:
        # Убираем ссылки, спецсимволы и лишние знаки разметки для естественной речи
        import re
        t = re.sub(r"https?://\S+", "", text)
        t = re.sub(r"[\*\_\[\]\(\)\{\}\<\>\#\`]", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _synthesize_and_play(self, text: str):
        with self.lock:
            temp_file = None
            try:
                self._ensure_mixer()
                # Создаем временный mp3 файл
                fd, temp_file = tempfile.mkstemp(suffix=".mp3")
                os.close(fd)

                async def _generate():
                    communicate = edge_tts.Communicate(text, self.voice)
                    await communicate.save(temp_file)

                # Запускаем генерацию речи
                asyncio.run(_generate())

                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    pygame.mixer.music.load(temp_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.05)
                    pygame.mixer.music.unload()
            except Exception as e:
                print(f"[Speaker] Ошибка озвучки: {e}")
            finally:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass

speaker = Speaker()
