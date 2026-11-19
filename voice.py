"""Free text-to-speech (Microsoft Edge voices, no key needed) with word timings."""
import asyncio

import edge_tts

import config


async def _run(text, out_mp3):
    voice, rate = config.get("TTS_VOICE"), config.get("TTS_RATE")
    try:
        comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    except TypeError:  # older edge-tts versions
        comm = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append((s, s + chunk["duration"] / 1e7, chunk["text"]))
    return words


def speak(text, out_mp3):
    """Returns list of (start_sec, end_sec, word)."""
    return asyncio.run(_run(text, str(out_mp3)))
