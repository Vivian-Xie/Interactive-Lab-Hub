NAME="${1:-Shirley}"
TEXT="Hello, ${NAME}! Welcome to Lab Three. Have fun with speech synthesis."
echo "$TEXT"

if command -v espeak >/dev/null 2>&1; then
  espeak "$TEXT"
elif command -v say >/dev/null 2>&1; then
  say "$TEXT"
else
  echo "[WARN] No TTS engine found (espeak/say)."
fi
