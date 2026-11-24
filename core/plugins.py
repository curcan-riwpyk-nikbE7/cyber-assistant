import os
import json

class PluginManager:
    """Менеджер плагинов и модулей расширений (как в Astra Plugin Store)."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        # Базовый каталог предустановленных и доступных плагинов
        self.plugins = [
            {
                "id": "browser_control",
                "name": "Web Browser & YouTube Control",
                "author": "Cyber Core",
                "version": "1.2.0",
                "desc": "Голосовой поиск в Google/Яндекс, открытие ссылок, запуск YouTube и поиск видео.",
                "icon": "🌐",
                "enabled": True,
                "category": "system"
            },
            {
                "id": "window_manager",
                "name": "Windows Desktop & Window Manager",
                "author": "WinAPI Tools",
                "version": "2.0.1",
                "desc": "Сворачивание всех окон (Win+D), закрытие программ, переключение между активными окнами.",
                "icon": "🗔",
                "enabled": True,
                "category": "system"
            },
            {
                "id": "media_sync",
                "name": "Spotify & Media Controls",
                "author": "Audio Team",
                "version": "1.4.0",
                "desc": "Управление громкостью, системный Mute, пауза, плей и переключение треков.",
                "icon": "🎵",
                "enabled": True,
                "category": "media"
            },
            {
                "id": "telegram_bridge",
                "name": "Telegram Remote Bridge",
                "author": "Community",
                "version": "0.9.5",
                "desc": "Удаленное управление домашним компьютером через Telegram-бота со смартфона.",
                "icon": "✈️",
                "enabled": False,
                "category": "network"
            },
            {
                "id": "obs_streamer",
                "name": "OBS Studio & Stream Deck",
                "author": "Stream Tools",
                "version": "1.1.0",
                "desc": "Голосовое переключение сцен в OBS, включение микрофона и запуск трансляции.",
                "icon": "🎙️",
                "enabled": False,
                "category": "streaming"
            },
            {
                "id": "game_booster",
                "name": "Steam & Game Launcher",
                "author": "Gaming Mode",
                "version": "1.0.4",
                "desc": "Автоматический запуск игр, очистка оперативной памяти и включение игрового режима.",
                "icon": "🎮",
                "enabled": True,
                "category": "gaming"
            }
        ]

    def get_plugins_list(self) -> list:
        return self.plugins

    def toggle_plugin(self, plugin_id: str) -> dict:
        for p in self.plugins:
            if p["id"] == plugin_id:
                p["enabled"] = not p["enabled"]
                return {"success": True, "plugin_id": plugin_id, "enabled": p["enabled"]}
        return {"success": False, "error": "Plugin not found"}
