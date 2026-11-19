"""Builds the vertical 1080x1920 video with FFmpeg: zooming scenes, voice, subtitles, music."""
import random
import shutil
import subprocess

import config

FPS = 30


def _check():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("FFmpeg is not installed or not on PATH. See README.")


def _run(args, cwd):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], cwd=cwd, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _ts(s):
    h, m = int(s // 3600), int(s % 3600 // 60)
    return f"{h}:{m:02d}:{s % 60:05.2f}"


def write_subs(words, total, narration, path, per_line=3):
    if not words:  # no timings: spread evenly
        ws = narration.split()
        step = total / max(len(ws), 1)
        words = [(i * step, (i + 1) * step, w) for i, w in enumerate(ws)]
    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial Black,88,&H00FFFFFF,&H0000FFFF,&H00000000,&H96000000,"
        "-1,0,0,0,100,100,0,0,1,7,3,5,70,70,0,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for i in range(0, len(words), per_line):
        group = words[i:i + per_line]
        end = words[i + per_line][0] if i + per_line < len(words) else group[-1][1] + 0.3
        text = " ".join(w[2] for w in group).upper().replace("{", "").replace("}", "")
        lines.append(f"Dialogue: 0,{_ts(group[0][0])},{_ts(end)},Default,,0,0,0,,{text}")
    path.write_text("\n".join(lines), encoding="utf-8")


def build(workdir, scenes, total, out_name="short.mp4"):
    _check()
    # scene length proportional to its number of words
    counts = [max(len(s["text"].split()), 1) for s in scenes]
    durs = [total * c / sum(counts) for c in counts]
    durs[-1] += 0.6  # small tail after the last word

    clips = []
    for i, d in enumerate(durs):
        frames = int(d * FPS) + 1
        zoom_in = i % 2 == 0
        z = "min(zoom+0.0009,1.18)" if zoom_in else "if(eq(on,0),1.18,max(zoom-0.0009,1.0))"
        vf = (f"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s=1080x1920:fps={FPS}")
        name = f"clip{i}.mp4"
        _run(["-i", f"scene{i}.png", "-vf", vf, "-frames:v", str(frames),
              "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", name], workdir)
        clips.append(name)

    (workdir / "list.txt").write_text("".join(f"file '{c}'\n" for c in clips), encoding="utf-8")
    _run(["-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "visual.mp4"], workdir)

    music = sorted(config.MUSIC_DIR.glob("*.mp3")) if config.MUSIC_DIR.exists() else []
    args = ["-i", "visual.mp4", "-i", "voice.mp3"]
    if music:
        args += ["-stream_loop", "-1", "-i", str(random.choice(music).resolve())]
        args += ["-filter_complex",
                 "[2:a]volume=0.12[m];[1:a][m]amix=inputs=2:duration=first[a];[0:v]ass=subs.ass[v]",
                 "-map", "[v]", "-map", "[a]"]
    else:
        args += ["-vf", "ass=subs.ass", "-map", "0:v", "-map", "1:a"]
    args += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-shortest", out_name]
    _run(args, workdir)

    for f in clips + ["visual.mp4", "list.txt"]:
        (workdir / f).unlink(missing_ok=True)
    return workdir / out_name
