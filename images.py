"""Scene images.
Order: OpenAI (paid, if key) -> Pollinations (FREE, no key) -> plain generated background.
Force one with IMAGE_PROVIDER=openai|pollinations|none"""
import base64
import io
import random
import time
import urllib.parse
import zlib

import requests
from PIL import Image, ImageDraw, ImageFilter

import config

W, H = 1080, 1920


def _openai(prompt, out):
    r = requests.post("https://api.openai.com/v1/images/generations", headers={
        "Authorization": f"Bearer {config.get('OPENAI_API_KEY')}",
    }, json={
        "model": config.get("OPENAI_IMAGE_MODEL"), "prompt": prompt,
        "size": "1024x1536", "n": 1,
    }, timeout=300)
    r.raise_for_status()
    item = r.json()["data"][0]
    if item.get("b64_json"):
        out.write_bytes(base64.b64decode(item["b64_json"]))
    else:
        out.write_bytes(requests.get(item["url"], timeout=120).content)


def _fallback(seed, out):
    rnd = random.Random(seed)
    c1 = [rnd.randint(10, 90) for _ in range(3)]
    c2 = [rnd.randint(60, 200) for _ in range(3)]
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    for _ in range(12):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(80, 320)
        g.ellipse([x - r, y - r, x + r, y + r], fill=tuple(rnd.randint(80, 255) for _ in range(3)))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    Image.blend(img, glow, 0.35).save(out, quality=92)


_last_call = [0.0]
_state = {"ok": 0, "disabled": False, "last_good": None}
RETRYABLE = {408, 425, 429, 500, 502, 503, 504, 530}


def _pollinations(prompt, out, seed, tries=4):
    """Free image service. Anonymous use is rate-limited, so we space requests out
    and back off when it says 'too many requests'.
    Optional free key: POLLINATIONS_API_KEY (enter.pollinations.ai) = faster + fewer limits."""
    key = config.get("POLLINATIONS_API_KEY")
    q = urllib.parse.quote(prompt[:800], safe="")
    params = {"width": W, "height": H, "nologo": "true", "seed": seed,
              "model": config.get("POLLINATIONS_MODEL") or "flux"}
    if key:
        url, headers, params = (f"https://gen.pollinations.ai/image/{q}",
                                {"Authorization": f"Bearer {key}"}, {**params, "key": key})
        gap = 3
    else:
        url, headers, gap = f"https://image.pollinations.ai/prompt/{q}", {}, 20
    last = "unknown error"
    for attempt in range(tries):
        wait = gap - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        _last_call[0] = time.time()
        try:
            r = requests.get(url, params=params, headers=headers, timeout=240)
            if r.status_code == 200:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                img.save(out, quality=92)
                return
            last = f"HTTP {r.status_code}: {r.text[:150]!r}"
            if r.status_code not in RETRYABLE:
                break  # e.g. 401/403 - waiting will not help
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:150]}"
        backoff = 30 * (attempt + 1)
        print(f"    image try {attempt + 1}/{tries} failed - {last} - waiting {backoff}s")
        time.sleep(backoff)
    raise RuntimeError(last)


def _reuse(out):
    """Use the last good AI image again (mirrored, so it looks different)."""
    img = Image.open(_state["last_good"]).convert("RGB").transpose(Image.FLIP_LEFT_RIGHT)
    img.save(out, quality=92)


def make(prompt, style, out, seed):
    full = f"{prompt}. Style: {style}. Vertical 9:16, no text, no letters."
    num_seed = zlib.crc32(str(seed).encode()) % 1_000_000
    provider = config.get("IMAGE_PROVIDER").lower()
    if not provider:
        provider = "openai" if config.get("OPENAI_API_KEY") else "pollinations"
    if provider == "openai":
        try:
            _openai(full, out)
            _state["last_good"] = out
            return
        except Exception as e:
            print(f"  OpenAI image failed ({e}), trying free Pollinations")
            provider = "pollinations"
    if provider == "pollinations" and not _state["disabled"]:
        try:
            _pollinations(full, out, num_seed)
            _state["ok"] += 1
            _state["last_good"] = out
            print(f"    image OK: {out.name}")
            return
        except Exception as e:
            print(f"  free image failed ({e})")
            if _state["ok"] == 0:  # never worked in this run -> don't keep waiting
                _state["disabled"] = True
    if _state["last_good"]:
        print(f"    reusing previous image for {out.name}")
        _reuse(out)
        return
    _fallback(seed, out)
