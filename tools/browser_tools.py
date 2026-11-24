import webbrowser
import urllib.parse

def open_url(url: str) -> bool:
    """Открывает указанный URL в браузере по умолчанию."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return webbrowser.open(url)

def search_internet(query: str, engine: str = "google") -> bool:
    """Выполняет поиск запроса в интернете."""
    q_encoded = urllib.parse.quote_plus(query)
    if engine.lower() == "yandex":
        url = f"https://yandex.ru/search/?text={q_encoded}"
    else:
        url = f"https://www.google.com/search?q={q_encoded}"
    return webbrowser.open(url)

def search_youtube(query: str) -> bool:
    """Ищет видео или музыку на YouTube."""
    q_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q_encoded}"
    return webbrowser.open(url)

if __name__ == "__main__":
    print("Browser tools initialized.")
