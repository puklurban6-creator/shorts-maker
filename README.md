# AI Shorts Maker

Naredi izvirne angleške zgodbe za YouTube Shorts. Iz YouTuba prebere samo naslove in število ogledov popularnih Shortsov, ugotovi, kaj deluje, in napiše **povsem novo** zgodbo. Nič se ne kopira in nič se ne prenaša.

**Privzeto je vse brezplačno:** Gemini piše zgodbe, Edge glas bere, AI slike riše brezplačni Pollinations (brez ključa). OpenAI slike so neobvezne in plačljive.

## Kako delujeta Claude Code in Colab skupaj

- **GitHub** hrani kodo.
- **Claude Code** ureja kodo (»dodaj to funkcijo«) in jo shrani na GitHub.
- **Google Colab** (`shorts_maker.ipynb`) vedno vzame najnovejšo kodo z GitHuba in brezplačno izdela videe. Deluje na telefonu.

## Izdelava videa na telefonu (Colab)

1. Brezplačen Gemini ključ: **aistudio.google.com** → *Get API key*.
2. Odpri **colab.research.google.com** → **GitHub** → vpiši svoje uporabniško ime → izberi `shorts-maker` → `shorts_maker.ipynb`.
   (Za zaseben repozitorij moraš Colabu dovoliti dostop do GitHuba ali pa ustvariti GitHub žeton, glej spodaj.)
3. V nastavitvah vpiši `REPO_URL`, izberi žanr in število videov.
4. Meni **Runtime → Run all**. Ob prvem zagonu prilepiš Gemini ključ in dovoliš dostop do Google Drive.
5. Video najdeš v aplikaciji **Google Drive** → `ShortsMaker/output`. Tapni video → ⋯ → *Pošlji kopijo* → *Shrani video*, nato ga naloži v YouTube.

**Da ključa ne vpisuješ vsakič:** v Colabu tapni ikono 🔑 (Secrets) na levi, dodaj `GEMINI_API_KEY` in vklopi *Notebook access*.

**Zaseben repozitorij:** na GitHubu ustvari žeton (Settings → Developer settings → Personal access tokens → Fine-grained, samo branje za `shorts-maker`) in ga v Colab Secrets shrani kot `GITHUB_TOKEN`. Lahko pa repozitorij nastaviš kot javen, saj v njem ni ključev.

## Ključi

| Ključ | Potreben? | Cena |
|---|---|---|
| `GEMINI_API_KEY` | Da (ali katerikoli drug za zgodbe) | Brezplačno |
| `GROQ_API_KEY` | Ne, rezerva za zgodbe | Brezplačno |
| `YOUTUBE_API_KEY` | Priporočeno, za trende | Brezplačno (console.cloud.google.com → YouTube Data API v3) |
| `ANTHROPIC_API_KEY` | Ne | Plačljivo |
| `OPENAI_API_KEY` | Ne, boljše AI slike | Plačljivo (brez njega rišejo brezplačno Pollinations) |

Ponudnika lahko izbereš z `LLM_PROVIDER=gemini|groq|anthropic|openai`.

## Zagon na računalniku (če ga kdaj imaš)

```
pip install -r requirements.txt     # potrebuješ tudi FFmpeg
python main.py setup                # vpis ključev v .env
python main.py make --genre horror --count 3
```

Žanri: `horror`, `funny`, `motivational`, `mystery`, `fantasy`, `scifi`, `wholesome` (ali svoj). Glasbo v ozadju dodaš tako, da MP3 datoteke daš v `music/` (na Drive: `ShortsMaker/music`), vendar samo glasbo brez avtorskih pravic, npr. iz YouTube Audio Library.

## Pravila YouTuba

- Pri realističnih AI slikah ob nalaganju vklopi **"Altered or synthetic content"**.
- Ne nalagaj velikih količin podobnih videov. Program si zapomni že narejene ideje, vseeno pa vsak video preglej in dodaj svoj vložek.
