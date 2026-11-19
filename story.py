"""Writes an ORIGINAL story inspired by what is trending (never copies it)."""
import difflib
import json

import requests

import config

SYSTEM = (
    "You write original, narrated YouTube Shorts stories in English. "
    "You study why popular videos work (hooks, pacing, emotion, twists) but you "
    "never retell, adapt or paraphrase anyone else's story. Every premise, "
    "character, name and twist you write is new."
)

PROMPT = """Genre: {genre}
Visual art style for all scenes: {style}

Popular Shorts right now (titles only, for pattern analysis):
{trends}

Ideas I already made (do NOT repeat them):
{history}

Step 1 (silently): figure out WHY the popular ones perform - hook style, emotion, topic, twist, pacing.
Step 2: write a brand-new ORIGINAL story that uses those patterns.

Hard rules:
- Do not retell, adapt or paraphrase any listed video. New premise, new characters, new twist.
- No real people, brands, or copyrighted characters.
- Narration 120-160 words (about 45-55 seconds when read aloud).
- First sentence is a hook under 12 words that makes people keep watching.
- End with a twist or satisfying punchline.
- Split the narration into 5-7 scenes; the scene texts joined together are the full narration.
- image_prompt: vivid vertical image description, no text or letters in the image.

Return ONLY valid JSON:
{{"title": "max 60 chars", "description": "1-2 sentences", "hashtags": ["#shorts", "..."],
  "scenes": [{{"text": "narration part", "image_prompt": "..."}}]}}"""


def _gemini(prompt):
    model = config.get("GEMINI_MODEL")
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": config.get("GEMINI_API_KEY")},
        json={
            "systemInstruction": {"parts": [{"text": SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 1.0},
        }, timeout=180)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def _openai_compatible(url, key, model, prompt):
    r = requests.post(url, headers={"Authorization": f"Bearer {key}"}, json={
        "model": model, "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}],
    }, timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _provider():
    forced = config.get("LLM_PROVIDER").lower()
    if forced:
        return forced
    for name, key in [("gemini", "GEMINI_API_KEY"), ("groq", "GROQ_API_KEY"),
                      ("anthropic", "ANTHROPIC_API_KEY"), ("openai", "OPENAI_API_KEY")]:
        if config.get(key):
            return name
    raise SystemExit("No story API key. Get a free one at aistudio.google.com")


def _ask(prompt):
    p = _provider()
    if p == "gemini":
        return _gemini(prompt)
    if p == "groq":
        return _openai_compatible("https://api.groq.com/openai/v1/chat/completions",
                                  config.get("GROQ_API_KEY"), config.get("GROQ_MODEL"), prompt)
    if p == "anthropic":
        r = requests.post("https://api.anthropic.com/v1/messages", headers={
            "x-api-key": config.get("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01", "content-type": "application/json",
        }, json={
            "model": config.get("ANTHROPIC_MODEL"), "max_tokens": 2000, "system": SYSTEM,
            "messages": [{"role": "user", "content": prompt}],
        }, timeout=180)
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    if p == "openai":
        return _openai_compatible("https://api.openai.com/v1/chat/completions",
                                  config.get("OPENAI_API_KEY"),
                                  config.get("OPENAI_TEXT_MODEL"), prompt)
    raise SystemExit(f"Unknown LLM_PROVIDER: {p}")


def _parse(text):
    start, end = text.find("{"), text.rfind("}")
    data = json.loads(text[start:end + 1])
    if not data.get("scenes"):
        raise ValueError("no scenes")
    return data


def _too_similar(title, trend_titles):
    t = title.lower()
    return any(difflib.SequenceMatcher(None, t, x.lower()).ratio() > 0.6 for x in trend_titles)


def write(genre, style, trends, history, tries=3):
    trend_txt = "\n".join(f"- {t['title']} ({t['views']:,} views)" for t in trends[:20]) \
        or "- (no data - use what you know performs well in this genre)"
    hist_txt = "\n".join(f"- {h}" for h in history[-40:]) or "- (none yet)"
    prompt = PROMPT.format(genre=genre, style=style, trends=trend_txt, history=hist_txt)
    titles = [t["title"] for t in trends] + history
    for attempt in range(tries):
        try:
            data = _parse(_ask(prompt))
        except (ValueError, json.JSONDecodeError):
            continue
        if not _too_similar(data["title"], titles):
            data["narration"] = " ".join(s["text"].strip() for s in data["scenes"])
            return data
        print("  idea too close to an existing video, rewriting...")
    raise RuntimeError("Could not get an original story, try again.")
