import json
import datetime as dt
from pathlib import Path
import srt
from pydub import AudioSegment
from utils import OUTPUT_DIR

WORDS_PER_LINE = 7

def pick_latest_base() -> str:
    wavs = sorted(OUTPUT_DIR.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not wavs:
        raise FileNotFoundError("Pas de .wav trouvé. Lance d'abord tts_piper.py")
    return wavs[0].stem


def load_timings(path: Path):
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        words = []
        for ev in data:
            if ev.get("type") == "word":
                words.append({
                    "word": ev.get("text", ""),
                    "start": float(ev.get("start", 0.0)),
                    "end": float(ev.get("end", 0.0)),
                })
        return words
    return None


def chunk_words(words):
    chunk = []
    for w in words:
        chunk.append(w)
        if len(chunk) >= WORDS_PER_LINE:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def make_srt_from_words(words):
    subs = []
    idx = 1
    for group in chunk_words(words):
        start = group[0]["start"]
        end = group[-1]["end"]
        text = " ".join([w["word"] for w in group])
        subs.append(srt.Subtitle(
            index=idx,
            start=dt.timedelta(seconds=start),
            end=dt.timedelta(seconds=end),
            content=text
        ))
        idx += 1
    return srt.compose(subs)


def make_srt_linear(text: str, duration_sec: float):
    words = text.split()
    n = max(1, len(words))
    avg_word = duration_sec / n

    subs = []
    idx = 1
    i = 0
    t = 0.0
    while i < n:
        group = words[i:i+WORDS_PER_LINE]
        group_dur = avg_word * len(group)
        start = t
        end = min(duration_sec, t + group_dur + 0.15)
        content = " ".join(group)
        subs.append(srt.Subtitle(
            index=idx,
            start=dt.timedelta(seconds=start),
            end=dt.timedelta(seconds=end),
            content=content
        ))
        t = end
        i += WORDS_PER_LINE
        idx += 1
    return srt.compose(subs)


def main():
    base = pick_latest_base()
    wav_path = OUTPUT_DIR / f"{base}.wav"
    story_path = OUTPUT_DIR / f"{base}.txt"
    timings_path = OUTPUT_DIR / f"{base}_timings.json"
    srt_path = OUTPUT_DIR / f"{base}.srt"

    audio = AudioSegment.from_wav(wav_path)
    duration_sec = len(audio) / 1000.0

    words = load_timings(timings_path)
    if words:
        srt_text = make_srt_from_words(words)
    else:
        text = story_path.read_text(encoding="utf-8")
        srt_text = make_srt_linear(text, duration_sec)

    srt_path.write_text(srt_text, encoding="utf-8")
    print(f"Subs: {srt_path}")


if __name__ == "__main__":
    main()
