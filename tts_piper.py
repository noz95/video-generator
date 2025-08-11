import json
import subprocess
from pathlib import Path
from utils import (OUTPUT_DIR, PIPER_MODEL, PIPER_CONFIG, PIPER_LENGTH, PIPER_SPK,
                   write_text, read_text)

# Lit output/*.txt et produit voice.wav + timings.json

def run_piper(text_path: Path, wav_path: Path, timings_path: Path):
    cmd = [
        "piper",
        "--model", str(PIPER_MODEL),
        "--config", str(PIPER_CONFIG),
        "--output_file", str(wav_path),
        "--length_scale", str(PIPER_LENGTH),
        "--speaker", str(PIPER_SPK),
        "--json",
    ]
    text = read_text(text_path)
    proc = subprocess.run(cmd, input=text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"Piper failed: {proc.stderr.decode('utf-8', 'ignore')}")
    # Piper émet des lignes JSON; on les regroupe en liste
    lines = [json.loads(l) for l in proc.stdout.decode("utf-8", "ignore").splitlines() if l.strip()]
    Path(timings_path).write_text(json.dumps(lines, ensure_ascii=False, indent=2), encoding="utf-8")


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
    print(f"Voice: {wav_path}\nTimings: {timings_path}")


if __name__ == "__main__":
    main()