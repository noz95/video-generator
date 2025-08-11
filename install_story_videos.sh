#!/usr/bin/env bash
set -euo pipefail
APP_DIR=/opt/story-videos

# 1) Paquets de base via APT
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
  git curl unzip ffmpeg python3 python3-venv python3-pip \
  python3-requests python3-pydub python3-dotenv || true

# srt via APT si dispo, sinon pip système
if ! sudo apt -y install python3-srt; then
  sudo -H python3 -m pip install --break-system-packages srt
fi

# 2) Piper TTS (on supprime l'éventuel paquet 'piper' erroné)
if dpkg -l | awk '{print $2}' | grep -qx "piper"; then
  sudo apt remove -y piper || true
fi
# Installe le binaire officiel
TMPDIR=$(mktemp -d)
cd "$TMPDIR"
wget -q https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
sudo install -m 0755 piper/piper /usr/local/bin/piper
sudo ln -sf /usr/local/bin/piper /usr/local/bin/piper-tts || true
cd - >/dev/null
rm -rf "$TMPDIR"
# Vérif : le bon piper expose --model
if ! piper --help 2>&1 | grep -q -- "--model"; then
  echo "[ERREUR] Le binaire 'piper' trouvé ne supporte pas --model. Vérifie PATH." >&2
  exit 1
fi

# 3) Ollama (script officiel — pas de paquet APT maintenu)
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
  sudo systemctl enable --now ollama
fi

# 4) Arborescence app
sudo mkdir -p "$APP_DIR"/{backgrounds,models,output}
sudo chown -R "$USER":"$USER" "$APP_DIR"

# 5) venv local
python3 -m venv "$APP_DIR/.venv"
source "$APP_DIR/.venv/bin/activate"
pip install -U pip
pip install requests pydub srt python-dotenv

# 6) .env par défaut
[ -f "$APP_DIR/.env" ] || cp "$APP_DIR/.env.example" "$APP_DIR/.env" || true

cat <<EOF

Installation terminée. Dépose les fichiers voix dans $APP_DIR/models :
  fr_FR-tom-medium.onnx
  fr_FR-tom-medium.onnx.json
Puis exécute :
  source $APP_DIR/.venv/bin/activate && python $APP_DIR/pipeline.py

EOF
