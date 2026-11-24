import os
import io
import time
import threading
import psutil
import telebot
from PIL import ImageGrab
from tools.telemetry import get_system_telemetry

class TelegramCompanion:
    """Удаленный ассистент-компаньон в Telegram (Astra Connect Style)."""

    def __init__(self, token: str = "", router=None):
        self.token = token
        self.router = router
        self.bot = None
        self._thread = None
        self._running = False

    def start(self, token: str = None):
        if token:
            self.token = token
        if not self.token:
            print("[TelegramCompanion] Токен не задан. Бот не запущен.")
            return

        try:
            self.bot = telebot.TeleBot(self.token)
            self._setup_handlers()
            self._running = True
            self._thread = threading.Thread(target=self._run_polling, daemon=True)
            self._thread.start()
            print("[TelegramCompanion] Telegram бот успешно запущен.")
        except Exception as e:
            print(f"[TelegramCompanion] Ошибка запуска бота: {e}")

    def _setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            text = (
                "👋 **Привет! Я твой Кибер (Telegram Companion).**\n\n"
                "Доступные команды управления ПК:\n"
                "• `/status` — Нагрузка CPU, GPU, ОЗУ и диск\n"
                "• `/screen` — Скриншот рабочего стола\n"
                "• `/desktop` — Свернуть все окна\n"
                "• `/say [текст]` — Озвучить сообщение на ПК\n"
                "• `/cmd [команда]` — Выполнить голосовую команду (громкость, браузер, LLM)"
            )
            self.bot.reply_to(message, text, parse_mode="Markdown")

        @self.bot.message_handler(commands=['status'])
        def send_status(message):
            st = get_system_telemetry()
            text = (
                f"🖥 **Статус ПК ({st['device_name']}):**\n"
                f"• ЦП: `{st['cpu_percent']}%` ({st['cpu_name']})\n"
                f"• ОЗУ: `{st['ram_used_gb']} / {st['ram_total_gb']} ГБ`\n"
                f"• Диск C: `{st['disk_free_gb']} ГБ свободно`\n"
                f"• ГПУ: `{st['gpu_name']}`"
            )
            self.bot.reply_to(message, text, parse_mode="Markdown")

        @self.bot.message_handler(commands=['screen', 'screenshot'])
        def send_screenshot(message):
            try:
                self.bot.send_chat_action(message.chat.id, 'upload_photo')
                screenshot = ImageGrab.grab()
                bio = io.BytesIO()
                bio.name = 'screen.png'
                screenshot.save(bio, 'PNG')
                bio.seek(0)
                self.bot.send_photo(message.chat.id, bio, caption="📸 Текущий снимок экрана ПК")
            except Exception as e:
                self.bot.reply_to(message, f"Ошибка создания скриншота: {e}")

        @self.bot.message_handler(commands=['desktop'])
        def send_desktop(message):
            if self.router:
                res = self.router.route_command("сверни всё", speak=True)
                self.bot.reply_to(message, res.get("reply", "Свернул окна."))
            else:
                self.bot.reply_to(message, "Маршрутизатор команд не подключен.")

        @self.bot.message_handler(commands=['say'])
        def speak_text(message):
            from core.speaker import speaker
            cmd_args = message.text.replace("/say", "").strip()
            if cmd_args:
                speaker.speak(cmd_args)
                self.bot.reply_to(message, f"🔊 Озвучил на ПК: «{cmd_args}»")
            else:
                self.bot.reply_to(message, "Использование: /say Привет, я дома!")

        @self.bot.message_handler(func=lambda msg: True)
        def handle_user_command(message):
            if self.router:
                res = self.router.route_command(message.text, speak=True)
                self.bot.reply_to(message, f"🤖 Кибер: {res.get('reply', 'Команда выполнена.')}")
            else:
                self.bot.reply_to(message, "Маршрутизатор команд не подключен.")

    def _run_polling(self):
        while self._running:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
            except Exception as e:
                time.sleep(3)
