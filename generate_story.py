import requests
import re
from pathlib import Path
from utils import (ROOT, OUTPUT_DIR, OLLAMA_HOST, OLLAMA_MODEL, WORDS_MIN,
                   WORDS_MAX, STYLE, LANG, write_text, write_json, slugify)

PROMPT_TMPL = (
    "Raconte en {lang} une histoire courte au style ‘confession Reddit’.\n"
    "Longueur: {minw}-{maxw} mots.\n"
    "Structure: Titre sur une ligne (commence par 'Titre:'), puis 'Histoire:' sur une seule section.\n"
    "Ton: conversationnel, accroche immédiate, pas de vulgarité, accessible à tous.\n"
    "Thème/style: {style}.\n"
)


def call_ollama(prompt: str) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.8}
    }
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data.get("response", "").strip()


def parse_story(text: str):
    title_match = re.search(r"^\s*Titre\s*:\s*(.+)$", text, re.I | re.M)
    story_match = re.search(r"^\s*Histoire\s*:\s*(.+)$", text, re.I | re.S)
    title = title_match.group(1).strip() if title_match else "Histoire courte"
    story = story_match.group(1).strip() if story_match else text.strip()
    return title, story


def main():
    prompt = PROMPT_TMPL.format(lang=LANG, minw=WORDS_MIN, maxw=WORDS_MAX, style=STYLE)
    raw = call_ollama(prompt)
    title, story = parse_story(raw)

    base = slugify(title)
    story_path = OUTPUT_DIR / f"{base or 'story'}.txt"
    meta_path = OUTPUT_DIR / f"{base or 'story'}_meta.json"

    write_text(story_path, story)
    write_json(meta_path, {"title": title, "lang": LANG, "style": STYLE})
    print(f"Story saved: {story_path}")


if __name__ == "__main__":
    main()
