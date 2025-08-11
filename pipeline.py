import subprocess
from pathlib import Path
from utils import OUTPUT_DIR

STEPS = [
    ["python", "generate_story.py"],
    ["python", "tts_piper.py"],
    ["python", "make_subs.py"],
    ["python", "render_ffmpeg.py"],
]


def run_step(cmd):
    print("\n==>", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cmd in STEPS:
        run_step(cmd)
    print("\nPipeline OK ✅")


if __name__ == "__main__":
    main()