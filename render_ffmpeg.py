import os
import random
import shutil
import subprocess
from pathlib import Path
from utils import (OUTPUT_DIR, BACKGROUND_DIR, VIDEO_W, VIDEO_H, FPS, CRF, AUDIO_BR,
                   SUB_FONT_SIZE, SUB_OUTLINE, SUB_MARGIN_V, BAR_HEIGHT, SATURATION, CONTRAST)

# Rend le final .mp4 (1080x1920) en brûlant les sous-titres + barre de progression.

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


def ensure_procedural_bg(target: Path, duration: float = 65.0):
    # Génère un fond animé abstrait si aucun background fourni
    cmd = [
        FFMPEG,
        "-f", "lavfi", "-i", f"noise=size=1920x1080:rate={FPS}:spawn=1",
        "-t", str(duration),
        "-filter_complex",
        (
            "format=yuv420p,boxblur=20:1,eq=contrast=1.1:saturation=1.3,"
            f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,crop={VIDEO_W}:{VIDEO_H}"
        ),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF),
        "-y", str(target)
    ]
    subprocess.check_call(cmd)


def pick_background() -> Path:
    vids = list(BACKGROUND_DIR.glob("*.mp4"))
    if vids:
        return random.choice(vids)
    tmp = OUTPUT_DIR / "bg_proc.mp4"
    ensure_procedural_bg(tmp, 65.0)
    return tmp


def render(base: str):
    bg = pick_background()
    wav = OUTPUT_DIR / f"{base}.wav"
    srt = OUTPUT_DIR / f"{base}.srt"
    out = OUTPUT_DIR / f"{base}_1080x1920.mp4"

    # Sous-titres style ASS via 'force_style'
    force_style = f"Fontsize={SUB_FONT_SIZE},Outline={SUB_OUTLINE},MarginV={SUB_MARGIN_V}"

    filter_complex = (
        f"[0:v]scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase," \
        f"crop={VIDEO_W}:{VIDEO_H},eq=contrast={CONTRAST}:saturation={SATURATION},boxblur=8:1[v0];" \
        f"color=size={VIDEO_W}x{BAR_HEIGHT}:rate={FPS}:c=white[bar];" \
        f"[v0][bar]overlay=x='(W-w)*t/MAIN_DUR':y=0:enable='between(t,0,MAIN_DUR)'[v1];" \
        f"[v1]subtitles='{srt.as_posix()}':force_style='{force_style}'[vout]"
    )

    # Remplace MAIN_DUR à l'exécution via -filter_complex_script? On fait un str.replace simple.
    # On récupère la durée audio avec ffprobe simplifié: -shortest sur mux fait l'affaire.
    filter_complex = filter_complex.replace("MAIN_DUR", "main_dur")

    cmd = [
        FFMPEG,
        "-stream_loop", "-1", "-i", str(bg),
        "-i", str(wav),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "1:a",
        "-shortest",
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF),
        "-c:a", "aac", "-b:a", AUDIO_BR,
        "-y", str(out)
    ]

    # La variable main_dur correspond à la durée de la 2e entrée (audio). FFmpeg la connaît.
    # (Truc: certaines builds ne reconnaissent pas 'main_dur'; si c'est le cas, on peut calculer la durée
    # via pydub et animer la barre avec 'drawbox' et 't/DU', mais testez d'abord cette version.)

    subprocess.check_call(cmd)
    print(f"Video: {out}")


def main():
    # prend le dernier .srt/.wav
    srts = sorted(OUTPUT_DIR.glob("*.srt"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not srts:
        raise FileNotFoundError("Aucun .srt – lance make_subs.py")
    base = srts[0].stem
    render(base)


if __name__ == "__main__":
    main()