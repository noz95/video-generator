#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/story-videos"
FALLBACK_VENV="/var/lib/story-videos/.venv"   # venv hors /opt si /opt est 'noexec'
REQS_FILE="$APP_DIR/requirements.txt"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

ensure_venv() {
  local target="$1"
  sudo apt update
  sudo DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-venv python3-pip python3-full
  mkdir -p "$(dirname "$target")"
  python3 -m venv "$target"
  chmod -R u+rwX,go-rwx "$target" || true
  # test d'exécution (échoue si 'noexec')
  if ! "$target/bin/python" -c "print('ok')" >/dev/null 2>&1; then
    return 1
  fi
  echo "$target"
}

# 1) Choisir un emplacement de venv exécutable
VENV_DIR="$APP_DIR/.venv"
if ! ensure_venv "$VENV_DIR"; then
  echo "[warn] VENV dans /opt non exécutable (noexec probable). Fallback vers $FALLBACK_VENV"
  VENV_DIR="$FALLBACK_VENV"
  ensure_venv "$VENV_DIR" >/dev/null
fi

# 2) Activer venv + dépendances
source "$VENV_DIR/bin/activate"
python -V
pip install -U pip
if [ -f "$REQS_FILE" ]; then
  pip install -r "$REQS_FILE"
else
  pip install requests pydub srt python-dotenv
fi

# 3) Vérifs outils
command -v ffmpeg >/dev/null || { echo "[ERREUR] FFmpeg manquant (apt install ffmpeg)"; exit 1; }

# 4) Détecter PIPER_BIN (sans sourcer .env)
if [ -f .env ]; then
  PIPER_FROM_ENV=$(grep -E "^PIPER_BIN=" .env | tail -n1 | cut -d= -f2- || true)
  if [ -n "${PIPER_FROM_ENV:-}" ]; then
    export PIPER_BIN="$PIPER_FROM_ENV"
  fi
fi
if [ -z "${PIPER_BIN:-}" ]; then
  for c in /usr/local/bin/piper/piper /usr/local/bin/piper /usr/bin/piper piper; do
    if { [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; } && "$c" --help 2>&1 | grep -q -- "--model"; then
      export PIPER_BIN="$c"
      break
    fi
  done
fi
echo "[info] VENV_DIR=$VENV_DIR"
echo "[info] PIPER_BIN=${PIPER_BIN:-(auto via PATH par le script Python)}"

# 5) Lancer la pipeline
python pipeline.py
