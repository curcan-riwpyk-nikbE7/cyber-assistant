import json
import urllib.request
import urllib.error

class LLMEngine:
    """Универсальный менеджер ИИ-интеллекта (Ollama Local / Google Gemini Flash)."""

    def __init__(self, provider: str = "ollama", model: str = "qwen2.5:3b", gemini_key: str = ""):
        self.provider = provider  # "ollama" или "gemini"
        self.model = model        # "qwen2.5:3b", "llama3.2:1b" или "gemini-2.5-flash"
        self.gemini_key = gemini_key
        self.ollama_url = "http://127.0.0.1:11434"
        self.system_prompt = (
            "Ты — Кибер, умный, верный и остроумный цифровой голосовой ассистент с искусственным интеллектом для KINGSAID. "
            "Отвечай кратко, емко, дружелюбно и по делу (максимум 2-3 предложения), так как твои ответы озвучиваются голосом."
        )

    def set_provider(self, provider: str, model: str = None, gemini_key: str = None):
        self.provider = provider
        if model:
            self.model = model
        if gemini_key is not None:
            self.gemini_key = gemini_key

    def ask(self, prompt: str) -> dict:
        """Отправляет запрос в выбранную нейросеть."""
        if self.provider == "gemini":
            return self._ask_gemini(prompt)
        else:
            return self._ask_ollama(prompt)

    def _ask_ollama(self, prompt: str) -> dict:
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.model if self.model else "qwen2.5:3b",
                "system": self.system_prompt,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 160,
                    "temperature": 0.7
                }
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
            
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                reply = raw.get("response", "").strip()
                if not reply:
                    reply = "Хм, нейросеть задумалась, сэр. Попробуйте еще раз."
                return {"reply": reply, "emotion": "happy", "provider": "Ollama (" + self.model + ")"}
        except urllib.error.URLError:
            return {
                "reply": "Ollama не запущена на вашем ПК, сэр. Включите Ollama в настройках или переключитесь на Gemini.",
                "emotion": "guilty",
                "provider": "ollama_offline"
            }
        except Exception as e:
            return {
                "reply": f"Ошибка ответа нейросети: {e}",
                "emotion": "guilty",
                "provider": "error"
            }

    def _ask_gemini(self, prompt: str) -> dict:
        if not self.gemini_key:
            return {
                "reply": "Для работы Gemini Cloud укажите API-ключ в настройках Кибера, сэр.",
                "emotion": "guilty",
                "provider": "gemini_no_key"
            }

        try:
            model_name = self.model if "gemini" in self.model else "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{self.system_prompt}\n\nПользователь: {prompt}\nКибер:"}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 200,
                    "temperature": 0.7
                }
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                candidates = raw.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    reply = "".join([p.get("text", "") for p in parts]).strip()
                    return {"reply": reply, "emotion": "happy", "provider": "Google Gemini Cloud"}
                return {"reply": "Не удалось разобрать ответ от Gemini Cloud, сэр.", "emotion": "guilty", "provider": "gemini"}
        except Exception as e:
            return {
                "reply": f"Ошибка соединения с Gemini Cloud: {e}",
                "emotion": "guilty",
                "provider": "gemini_error"
            }
