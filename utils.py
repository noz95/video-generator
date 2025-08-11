import os
import json
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path("/opt/story-videos")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", ROOT / "output"))
BACKGROUND_DIR = Path(os.getenv("BACKGROUND_DIR", ROOT / "backgrounds"))

VIDEO_W = int(os.getenv("VIDEO_WIDTH", 1080))
VIDEO_H = int(os.getenv("VIDEO_HEIGHT", 1920))
FPS = int(os.getenv("FPS", 30))
CRF = int(os.getenv("CRF", 20))
AUDIO_BR = os.getenv("AUDIO_BITRATE", "128k")

SUB_FONT_SIZE = int(os.getenv("SUB_FONT_SIZE", 28))
SUB_OUTLINE = int(os.getenv("SUB_OUTLINE", 2))
SUB_MARGIN_V = int(os.getenv("SUB_MARGIN_V", 70))
BAR_HEIGHT = int(os.getenv("BAR_HEIGHT", 10))
SATURATION = float(os.getenv("SATURATION", 1.2))
CONTRAST = float(os.getenv("CONTRAST", 1.05))

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
LANG = os.getenv("STORY_LANGUAGE", "fr")
WORDS_MIN = int(os.getenv("STORY_WORDS_MIN", 120))
WORDS_MAX = int(os.getenv("STORY_WORDS_MAX", 160))
STYLE = os.getenv("STORY_GEN_STYLE", "confession reddit, twist léger")

PIPER_MODEL = Path(os.getenv("PIPER_MODEL_PATH", ROOT / "models" / "fr_FR-tom-medium.onnx"))
PIPER_CONFIG = Path(os.getenv("PIPER_CONFIG_PATH", ROOT / "models" / "fr_FR-tom-medium.onnx.json"))
PIPER_LENGTH = float(os.getenv("PIPER_LENGTH_SCALE", 1.0))
PIPER_SPK = int(os.getenv("PIPER_SPEAKER_ID", 0))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)


def choose_background():
    vids = list(BACKGROUND_DIR.glob("*.mp4"))
    return random.choice(vids) if vids else None


def write_text(path: Path, text: str):
    path.write_text(text.strip(), encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(title: str) -> str:
    keep = [c if c.isalnum() else "-" for c in title.lower()]
    s = "".join(keep)
    return "-".join([t for t in s.split("-") if t])[:80]
