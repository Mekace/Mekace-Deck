import json
import os

CONFIG_FILE = "config.json"
DEFAULT_SYSTEM_PROMPT = (
    "You are a senior software developer. Respond with concise, clean, "
    "and directly runnable code examples."
)


def load_config() -> dict:
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "api_key" in data and not data.get("gemini_key"):
                    data["gemini_key"] = data["api_key"]
                config = data
        except Exception:
            config = {}

    config.setdefault("language", "en")
    config.setdefault("system_prompt", DEFAULT_SYSTEM_PROMPT)
    config.setdefault("max_tokens", 4096)
    return config


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)