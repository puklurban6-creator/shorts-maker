# AI Shorts Maker

Naredi izvirne angleške zgodbe za YouTube Shorts. Iz YouTuba prebere samo naslove in število ogledov popularnih Shortsov, ugotovi, kaj deluje, in napiše **povsem novo** zgodbo. Nič se ne kopira in nič se ne prenaša.

## 1. Namestitev (enkrat)

1. Namesti **Python 3.10+**: https://www.python.org (na Windows obkljukaj "Add Python to PATH").
2. Namesti **FFmpeg**:
   - Windows: `winget install ffmpeg`
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. V tej mapi zaženi:
   ```
   pip install -r requirements.txt
   ```

## 2. API ključi

```
python main.py setup
```
Program te vpraša za ključe in jih shrani v datoteko `.env` (ne deli je z nikomer).

| Ključ | Ali je potreben | Kje ga dobiš |
|---|---|---|
| `ANTHROPIC_API_KEY` ali `OPENAI_API_KEY` | **Da, vsaj enega** (piše zgodbe) | console.anthropic.com / platform.openai.com |
| `YOUTUBE_API_KEY` | Priporočeno (trendi) | console.cloud.google.com, omogoči "YouTube Data API v3", brezplačno |
| `OPENAI_API_KEY` | Neobvezno (AI slike) | Brez njega program naredi abstraktna ozadja |

Glas je brezplačen (Microsoftovi Edge glasovi), ključ ni potreben.

## 3. Uporaba

```
python main.py trends --genre horror           # kaj je trenutno popularno
python main.py make --genre horror --count 3   # naredi 3 videe
python main.py make --genre funny --style "pixel art, retro"
```

Žanri: `horror`, `funny`, `motivational`, `mystery`, `fantasy`, `scifi`, `wholesome` (ali katerikoli svoj).

Vsak video se shrani v `output/<datum-naslov>/`:
- `short.mp4`: gotov video 1080x1920
- `upload_info.txt`: naslov, opis, hashtagi za YouTube

**Glasba v ozadju:** v mapo `music/` daj svoje MP3 datoteke (samo glasbo brez avtorskih pravic, npr. iz YouTube Audio Library).

## 4. Nastavitve v `.env`

- `TTS_VOICE` npr. `en-US-AriaNeural`, `en-GB-RyanNeural` (seznam: `edge-tts --list-voices`)
- `TTS_RATE` hitrost govora, npr. `+10%`
- `ANTHROPIC_MODEL`, `OPENAI_TEXT_MODEL`, `OPENAI_IMAGE_MODEL`, `REGION`

## 5. Pravila YouTuba

- Pri realističnih AI slikah ob nalaganju vklopi **"Altered or synthetic content"**.
- Ne nalagaj velikih količin enakih videov naenkrat. Program si zapomni že narejene ideje (`history.json`), vseeno pa preglej vsak video in dodaj svoj vložek, sicer lahko izgubiš unovčevanje.
