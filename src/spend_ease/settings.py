import json
from pathlib import Path

DEFAULT_PATH = Path.home() / ".spend_ease" / "settings.json"


def save_setting(key: str, value: float) -> None:
    settings = load_settings()
    settings[key] = value
    
    DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_PATH, "w") as f:
        json.dump(settings, f, indent=2)


def load_settings() -> dict:
    if not DEFAULT_PATH.exists():
        return {}
    
    with open(DEFAULT_PATH, "r") as f:
        return json.load(f)


def get_setting(key: str, default: float = 0.0) -> float:
    settings = load_settings()
    return settings.get(key, default)
