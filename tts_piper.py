import os
import json
import shutil
import subprocess
from pathlib import Path
from utils import (
    OUTPUT_DIR,
    PIPER_MODEL,
    PIPER_CONFIG,
    PIPER_LENGTH,
    PIPER_SPK,
    read_text,
)

def find_piper_cmd():
    candidates = [
        os.getenv("PIPER_BIN", "piper"),
        "piper",
        "piper-tts",
        "piper-tts-cli",
        str(shutil.which("piper") or ""),
        str(shutil.which("piper-tts") or ""),
        str(shutil.which("piper-tts-cli") or ""),
    ]
    seen = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        try:
            out = subprocess.run([c, "--help"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if out.returncode == 0 and "--model" in out.stdout:
                return c
        except FileNotFoundError:
            pass
    raise RuntimeError("Aucun binaire Piper compatible ('--model') trouvé. Réinstalle Piper TTS ou pointe PIPER_BIN.")

def run_piper(text_path: Path, wav_path: Path, timings_path: Path):
    piper_cmd = find_piper_cmd()
    cmd = [
        piper_cmd,
        "--model", str(PIPER_MODEL),
        "--config", str(PIPER_CONFIG),
        "--output_file", str(wav_path),
        "--length_scale", str(PIPER_LENGTH),
        "--speaker", str(PIPER_SPK),
        "--json",
    ]
    text = read_text(text_path)
    proc = subprocess.run(cmd, input=text.encode("utf-8"),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"Piper failed: {proc.stderr.decode('utf-8', 'ignore')}")

    # Parse robuste: ne garder que les lignes JSON
    raw_lines = proc.stdout.decode("utf-8", "ignore").splitlines()
    events = []
    for line in raw_lines:
        s = line.strip()
        if not s or s[0] not in "{[":
            continue
        try:
            obj = json.loads(s)
            events.append(obj)
        except Exception:
            continue

    timings_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")

def pick_latest_story() -> Path:
    txts = sorted(OUTPUT_DIR.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not txts:
        raise FileNotFoundError("Aucune histoire .txt trouvée dans output/")
    return txts[0]

def main():
    story_path = pick_latest_story()
    base = story_path.stem
    wav_path = OUTPUT_DIR / f"{base}.wav"
    timings_path = OUTPUT_DIR / f"{base}_timings.json"
    run_piper(story_path, wav_path, timings_path)
    print(f"Voice: {wav_path}")
    print(f"Timings: {timings_path}")

if __name__ == "__main__":
    main()

