import os
import sys
import yaml
from core.router import CommandRouter

def load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

def main():
    config = load_config()
    bot_name = config.get("assistant", {}).get("name", "Кибер")
    print(f"==================================================")
    print(f"   CYBER ASSISTANT (Кибер) // KINGSAID EDITION    ")
    print(f"==================================================")
    print(f"[*] Инициализация ядра...")
    print(f"[*] Ассистент: {bot_name}")
    print(f"[*] Слово активации: {config.get('assistant', {}).get('wake_words', ['кибер'])}")
    print(f"[*] Хоткей: {config.get('assistant', {}).get('hotkey', 'alt+space')}")
    print(f"[*] Роутер команд готов. Нажмите Ctrl+C для выхода.\n")

    router = CommandRouter()

    # Демонстрационный цикл консольного тестирования команд
    test_phrases = [
        "Кибер, как дела и какая нагрузка?",
        "Кибер, поставь музыку на паузу",
        "Кибер, открой браузер"
    ]

    print("[*] Тестирование распознанных команд:")
    for phrase in test_phrases:
        print(f"\n[Ввод] > {phrase}")
        res = router.route_command(phrase)
        print(f"[Кибер ({res['emotion']})] > {res['reply']}")

    print("\n[+] Базовая структура ядра и роутера проверена успешно!")

if __name__ == "__main__":
    main()
