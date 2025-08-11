# Story Video Generator – README

### Prérequis système
- Ubuntu 22.04+ (ou Debian/AlmaLinux équivalent)
- Python 3.10+
- FFmpeg installé (avec libx264 + aac)
- Ollama installé et modèle téléchargé (ex: llama3.2)
- Piper TTS installé + un modèle de voix FR ou EN

### Installation rapide

# 1) FFmpeg
sudo apt-get update && sudo apt-get install -y ffmpeg

# 2) Ollama (voir https://ollama.com/download)
curl -fsSL https://ollama.com/install.sh | sh
# Lancer Ollama en service (ou `ollama serve` dans un screen/tmux)
sudo systemctl enable --now ollama
# Télécharger un modèle (ex)
ollama pull llama3.2

# 3) Piper TTS (binaire)
# Voir releases: https://github.com/rhasspy/piper/releases
# Exemple rapide Ubuntu:
sudo apt-get install -y unzip
wget -O piper_linux_x86_64.tar.gz \
  https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
sudo tar -xzf piper_linux_x86_64.tar.gz -C /usr/local/bin --strip-components=1 piper/piper
# Vérifier
type piper

# 4) Modèles Piper (voix)
# Exemples FR (choisir l'un):
# https://github.com/rhasspy/piper/blob/master/VOICES.md
# Placez les fichiers modèle (.onnx et .json) dans models/

# 5) Projet Python
cd story-videos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
mkdir -p backgrounds models output

# 6) Test de bout en bout
python pipeline.py

### Conseils
- Placez 2–3 boucles mp4 dans backgrounds/ (pixabay/pexels libres de droit).
- Ajustez `.env` pour la langue, vitesse, modèle, longueur d'histoire.
- Si aucun fond n'est présent, on génère un fond procédural avec FFmpeg.