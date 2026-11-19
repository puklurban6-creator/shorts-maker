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


def _pollinations(prompt, out, seed, tries=3):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:900])
    params = {"width": W, "height": H, "nologo": "true", "seed": seed,
              "model": config.get("POLLINATIONS_MODEL") or "flux"}
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(url, params=params, timeout=180)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")  # fails if not an image
            img.save(out, quality=92)
            return
        except Exception as e:
            last = e
            time.sleep(5 * (attempt + 1))  # free service: be gentle, wait and retry
    raise RuntimeError(last)


def make(prompt, style, out, seed):
    full = f"{prompt}. Style: {style}. Vertical 9:16, no text, no letters."
    num_seed = zlib.crc32(str(seed).encode()) % 1_000_000
    provider = config.get("IMAGE_PROVIDER").lower()
    if not provider:
        provider = "openai" if config.get("OPENAI_API_KEY") else "pollinations"
    if provider == "openai":
        try:
            _openai(full, out)
            return
        except Exception as e:
            print(f"  OpenAI image failed ({e}), trying free Pollinations")
            provider = "pollinations"
    if provider == "pollinations":
        try:
            _pollinations(full, out, num_seed)
            return
        except Exception as e:
            print(f"  free image service failed ({e}), using plain background")
    _fallback(seed, out)
