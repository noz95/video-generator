import random
import shutil
import subprocess
from pathlib import Path
from pydub import AudioSegment
from utils import (
    OUTPUT_DIR, BACKGROUND_DIR, VIDEO_W, VIDEO_H, FPS, CRF, AUDIO_BR,
    SUB_FONT_SIZE, SUB_OUTLINE, SUB_MARGIN_V, BAR_HEIGHT, SATURATION, CONTRAST
)

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

def ensure_procedural_bg(target: Path, duration: float = 65.0):
    # Fond procédural simple: noir + bruit + blur + léger boost de saturation
    vf = (
        "noise=alls=12:allf=t+u,"
        "boxblur=20:1,"
        "eq=contrast=1.1:saturation=1.3,"
        "format=yuv420p"
    )
    cmd = [
        FFMPEG,
        "-f", "lavfi",
        "-i", f"color=c=black:s={VIDEO_W}x{VIDEO_H}:r={FPS}",
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF),
        "-y", str(target),
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

    dur = len(AudioSegment.from_wav(wav)) / 1000.0
    force_style = f"Fontsize={SUB_FONT_SIZE},Outline={SUB_OUTLINE},MarginV={SUB_MARGIN_V}"
    srt_path = srt.as_posix()

    # Chaîne de filtres robuste :
    # [0:v]=fond, [1:a]=voix, [2:v]=barre blanche à la bonne hauteur
    filter_complex = (
        # Base habillée
        f"[0:v]scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_W}:{VIDEO_H},eq=contrast={CONTRAST}:saturation={SATURATION},"
        f"boxblur=8:1[base];"
        # Barre : rogner la source blanche selon le temps (virgule échappée)
        f"[2:v]crop=w=iw*min(t/{dur}\\,1):h=ih:x=0:y=0[barc];"
        # Superpose la barre puis les sous-titres
        f"[base][barc]overlay=x=0:y=0[withbar];"
        f"[withbar]subtitles='{srt_path}':force_style='{force_style}'[vout]"
    )

    cmd = [
        FFMPEG,
        "-stream_loop", "-1", "-i", str(bg),                     # 0:v
        "-i", str(wav),                                         # 1:a
        "-f", "lavfi", "-i", f"color=size={VIDEO_W}x{BAR_HEIGHT}:rate={FPS}:c=white",  # 2:v
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "1:a",
        "-shortest",
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF),
        "-c:a", "aac", "-b:a", AUDIO_BR,
        "-y", str(out),
    ]
    subprocess.check_call(cmd)
    print(f"Video: {out}")

def main():
    srts = sorted(OUTPUT_DIR.glob("*.srt"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not srts:
        raise FileNotFoundError("Aucun .srt – lance make_subs.py")
    base = srts[0].stem
    render(base)

if __name__ == "__main__":
    main()

