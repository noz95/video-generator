apt update && apt install -y wget tar ca-certificates

cd /tmp
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64) ASSET=piper_linux_x86_64.tar.gz ;;
  aarch64|arm64) ASSET=piper_linux_aarch64.tar.gz ;;
  *) echo "Arch non prise en charge: $ARCH" && exit 1 ;;
esac

curl -L -o piper.tgz "https://github.com/rhasspy/piper/releases/latest/download/${ASSET}"
tar -xzf piper.tgz
install -m 0755 piper/piper /usr/local/bin/piper
hash -r

# Doit afficher l’option --model
/usr/local/bin/piper --help | grep -- --model

