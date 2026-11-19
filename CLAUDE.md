# AI Shorts Maker - notes for Claude Code

The owner works only from an iPhone (no computer) and speaks Slovenian - reply in Slovenian, keep steps phone-friendly.

## How the project is used
- Code is edited here (Claude Code / GitHub).
- Videos are made in **Google Colab** with `shorts_maker.ipynb`, which `git clone`/`git pull`s this repo, installs `requirements.txt` and runs `python main.py make ...`.
- So: every change must still work when run from the notebook. If you change commands, settings or file names, update `shorts_maker.ipynb` and `README.md` too.

## Structure
- `main.py` - CLI: `setup`, `trends`, `make --genre X --count N --style "..."`
- `trends.py` - YouTube Data API, reads only titles/views (never downloads videos)
- `story.py` - writes ORIGINAL stories; providers: Gemini (free, default) -> Groq -> Anthropic -> OpenAI, or force with `LLM_PROVIDER`
- `voice.py` - free Edge TTS with word timings
- `images.py` - OpenAI images if key, else FREE Pollinations (no key), else plain generated backgrounds; force with `IMAGE_PROVIDER`
- `video.py` - FFmpeg: Ken Burns scenes, ASS subtitles, optional music, 1080x1920
- `config.py` - keys from env / `.env`; `SHORTS_OUTPUT_DIR`, `SHORTS_HISTORY_FILE`, `SHORTS_MUSIC_DIR` overrides

## Rules
- Never commit API keys or `.env` (add a `.gitignore` with `.env`, `output/`, `__pycache__/`, `history.json` if missing).
- Never add features that download, re-upload or copy other people's videos, audio or scripts. Trends are for inspiration only.
- Keep it free to run by default (Gemini + Edge TTS + generated images).
- To test without paid keys: generate sample images with `images._fallback`, a sine-wave `voice.mp3` with ffmpeg, and call `video.build`.
