"""Loads API keys and settings from the .env file next to this script."""
import os
from getpass import getpass
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENV_FILE = BASE / ".env"
OUTPUT_DIR = BASE / "output"
MUSIC_DIR = BASE / "music"
HISTORY_FILE = BASE / "history.json"

KEYS = [
    ("YOUTUBE_API_KEY", "YouTube Data API key (for trend ideas, optional)"),
    ("ANTHROPIC_API_KEY", "Anthropic (Claude) API key - writes the stories"),
    ("OPENAI_API_KEY", "OpenAI API key - AI images (and stories if no Claude key)"),
]

DEFAULTS = {
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
    if not (values["ANTHROPIC_API_KEY"] or values["OPENAI_API_KEY"]):
        print("WARNING: you need at least an Anthropic or OpenAI key to write stories.")
