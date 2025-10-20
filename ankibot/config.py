"""
Configuration management for Ankibot
"""

import os
import json
from typing import Any, Dict

APP_TITLE = "Ankibot – Flashcard Generator"
CONFIG_FILE = "config.json"
DEFAULT_MODEL = "gemini-2.5-flash"


def load_config() -> Dict[str, Any]:
    """Load configuration from disk or environment defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Default config if file not found
    return {
        "api_key": "",
        "theme": "system",
        "accent": "#40C4FF",
        "model_mode": "Fast (Gemini 2.5 Flash + thinking)",
        "reverse": False,
        "density": 2,
        "split_by_topic": False,
    }



def save_config(cfg: Dict[str, Any]) -> None:
    """Persist configuration to disk."""
    config_dir = os.path.dirname(CONFIG_FILE)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print(f"Configuration saved to {CONFIG_FILE}")
