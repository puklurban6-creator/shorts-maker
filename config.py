"""Loads API keys and settings from the .env file next to this script."""
import os
from getpass import getpass
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENV_FILE = BASE / ".env"
# Colab (or anything else) can redirect output/history, e.g. to Google Drive.
OUTPUT_DIR = Path(os.environ.get("SHORTS_OUTPUT_DIR", BASE / "output"))
MUSIC_DIR = Path(os.environ.get("SHORTS_MUSIC_DIR", BASE / "music"))
HISTORY_FILE = Path(os.environ.get("SHORTS_HISTORY_FILE", BASE / "history.json"))

# Story writers, tried in this order (first key found wins, free ones first).
# Force one with LLM_PROVIDER=gemini|groq|anthropic|openai
KEYS = [
    ("GEMINI_API_KEY", "Google Gemini API key - FREE, writes the stories (aistudio.google.com)"),
    ("GROQ_API_KEY", "Groq API key - FREE alternative story writer (optional)"),
    ("YOUTUBE_API_KEY", "YouTube Data API key - FREE, trend ideas (optional)"),
    ("ANTHROPIC_API_KEY", "Anthropic (Claude) API key - paid story writer (optional)"),
    ("OPENAI_API_KEY", "OpenAI API key - paid AI images (optional)"),
]

DEFAULTS = {
    "GEMINI_MODEL": "gemini-flash-latest",
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "ANTHROPIC_MODEL": "claude-sonnet-5-5",
    "OPENAI_TEXT_MODEL": "gpt-4o-mini",
    "OPENAI_IMAGE_MODEL": "gpt-image-1",
    "TTS_VOICE": "en-US-ChristopherNeural",
    "TTS_RATE": "+8%",
    "REGION": "US",
}


def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    for k, v in DEFAULTS.items():
        os.environ.setdefault(k, v)


def get(name):
    return os.environ.get(name, "").strip()


def setup():
    """Interactive prompt that saves keys into .env."""
    load_env()
    print("Paste your API keys. Press Enter to keep the current value / skip.\n")
    values = {}
    for name, label in KEYS:
        cur = get(name)
        shown = f" [current: ...{cur[-4:]}]" if cur else ""
        new = getpass(f"{label}{shown}: ").strip()
        values[name] = new or cur
    for k, v in DEFAULTS.items():
        values.setdefault(k, get(k) or v)
    ENV_FILE.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")
    print(f"\nSaved to {ENV_FILE}")
    if not any(values[k] for k in ("GEMINI_API_KEY", "GROQ_API_KEY",
                                    "ANTHROPIC_API_KEY", "OPENAI_API_KEY")):
        print("WARNING: you need a story key - get a free Gemini key at aistudio.google.com")
