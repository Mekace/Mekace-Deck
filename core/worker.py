import json
import time
import urllib.error
import urllib.request
from PySide6.QtCore import QThread, Signal
from core.providers import PROVIDERS


class AIWorker(QThread):
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        provider: str,
        model: str,
        budget: int,
        api_key: str,
        history: list[dict],
        system_prompt: str,
        max_tokens: int,
        chat_session=None,
        user_message: str = "",
    ):
        super().__init__()
        self.provider = provider
        self.model = model
        self.budget = budget
        self.api_key = api_key
        self.history = history
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.chat_session = chat_session
        self.user_message = user_message

    def run(self):
        if self.provider == "Gemini":
            self._run_gemini()
        else:
            self._run_openai_compatible()

    def _run_gemini(self):
        for attempt in range(3):
            try:
                response = self.chat_session.send_message(self.user_message)
                self.response_ready.emit(response.text)
                return
            except Exception as e:
                if "503" in str(e) and attempt < 2:
                    time.sleep(2)
                    continue
                self.error_occurred.emit(str(e))
                return

    def _run_openai_compatible(self):
        url = PROVIDERS[self.provider]["endpoint"]
        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": self.max_tokens,
        }
        if self.provider == "OpenRouter" and self.budget > 0 and "reasoning" in self.model:
            payload["reasoning"] = {"max_tokens": self.budget}

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MekacesDeck/1.0",
        }
        if self.provider == "OpenRouter":
            headers["HTTP-Referer"] = "http://localhost"
            headers["X-Title"] = "Mekace's Deck"

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    if "error" in body:
                        err_val = body["error"]
                        msg = err_val.get("message", str(err_val)) if isinstance(err_val, dict) else str(err_val)
                        self.error_occurred.emit(msg)
                        return
                    reply = body["choices"][0]["message"]["content"]
                    self.response_ready.emit(reply)
                    return
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                if e.code in (429, 502, 503) and attempt < 2:
                    time.sleep(2)
                    continue
                try:
                    err_json = json.loads(err_body)
                    err_obj = err_json.get("error", {})
                    msg = err_obj.get("metadata", {}).get("raw") or err_obj.get("message") or err_body
                except Exception:
                    msg = err_body
                self.error_occurred.emit(f"HTTP {e.code}: {msg}")
                return