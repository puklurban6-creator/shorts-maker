"""AI Shorts Maker - original English story Shorts inspired by trends.

  python main.py setup                              # save API keys
  python main.py trends --genre horror              # see what is popular
  python main.py make --genre horror --count 3      # make 3 videos
"""
import argparse
import json
import re
from datetime import datetime

import config

STYLES = {
    "horror": "dark cinematic digital painting, moody lighting, fog",
    "funny": "bright colorful 3D cartoon, expressive characters",
    "motivational": "cinematic photo-realistic, golden hour light",
    "mystery": "noir illustration, deep shadows, rain",
    "fantasy": "epic fantasy concept art, glowing magic",
    "scifi": "futuristic sci-fi concept art, neon",
    "wholesome": "soft watercolor illustration, warm colors",
}


def load_history():
    if config.HISTORY_FILE.exists():
        return json.loads(config.HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(h):
    config.HISTORY_FILE.write_text(json.dumps(h, indent=2), encoding="utf-8")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "short"


def make_one(genre, style, trends):
    import images, story, video, voice  # imported here so `setup` works before installing

    history = load_history()
    print("1/4 Writing original story...")
    s = story.write(genre, style, trends, history)
    print(f"    -> {s['title']}")

    work = config.OUTPUT_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-{slug(s['title'])}"
    work.mkdir(parents=True, exist_ok=True)

    print("2/4 Recording voice...")
    words = voice.speak(s["narration"], work / "voice.mp3")
    total = video.duration(work / "voice.mp3")

    print(f"3/4 Making {len(s['scenes'])} images...")
    for i, sc in enumerate(s["scenes"]):
        images.make(sc["image_prompt"], style, work / f"scene{i}.png", seed=f"{s['title']}{i}")

    print("4/4 Building video...")
    video.write_subs(words, total, s["narration"], work / "subs.ass")
    out = video.build(work, s["scenes"], total)

    (work / "upload_info.txt").write_text(
        f"TITLE:\n{s['title']}\n\nDESCRIPTION:\n{s.get('description', '')}\n\n"
        f"{' '.join(s.get('hashtags', ['#shorts']))}\n\nSCRIPT:\n{s['narration']}\n\n"
        "UPLOAD CHECKLIST:\n- If images look realistic, turn on 'Altered or synthetic content'.\n"
        "- Not made for kids (unless it really is).\n", encoding="utf-8")
    (work / "story.json").write_text(json.dumps(s, indent=2), encoding="utf-8")

    history.append(s["title"])
    save_history(history)
    print(f"Done: {out}  ({total:.0f}s)\n")


def main():
    config.load_env()
    p = argparse.ArgumentParser(description="AI Shorts Maker")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup", help="enter and save API keys")
    t = sub.add_parser("trends", help="show popular Shorts titles")
    t.add_argument("--genre", default="scary")
    m = sub.add_parser("make", help="create videos")
    m.add_argument("--genre", default="horror", help=f"e.g. {', '.join(STYLES)}")
    m.add_argument("--count", type=int, default=1)
    m.add_argument("--style", help="custom art style for images")
    a = p.parse_args()

    if a.cmd == "setup":
        config.setup()
        return

    import trends
    if a.cmd == "trends":
        for x in trends.fetch(a.genre):
            print(f"{x['views']:>12,}  {x['title']}")
        return

    style = a.style or STYLES.get(a.genre, "cinematic digital illustration")
    print(f"Checking trends for '{a.genre}'...")
    data = trends.fetch(a.genre)
    for n in range(a.count):
        print(f"=== Video {n + 1}/{a.count} ===")
        make_one(a.genre, style, data)


if __name__ == "__main__":
    main()
