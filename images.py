"""Scene images: OpenAI if a key exists, otherwise free generated backgrounds."""
import base64
import random

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


def make(prompt, style, out, seed):
    if config.get("OPENAI_API_KEY"):
        try:
            _openai(f"{prompt}. Style: {style}. Vertical 9:16, no text, no letters.", out)
            return
        except Exception as e:
            print(f"  image API failed ({e}), using fallback background")
    _fallback(seed, out)
