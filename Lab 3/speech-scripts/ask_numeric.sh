PROMPT="${1:-Please enter your 5 digit ZIP code}"
LABEL="${2:-zipcode}"
LOG_FILE="../responses.csv"

# Speak prompt
echo "$PROMPT"
if command -v espeak >/dev/null 2>&1; then
  espeak "$PROMPT"
elif command -v say >/dev/null 2>&1; then
  say "$PROMPT"
fi
read -r USER_INPUT
if [[ "$USER_INPUT" =~ ^[0-9]+$ ]]; then
  TS="$(date -Iseconds)"
  [ -f "$LOG_FILE" ] || echo "timestamp,label,value" > "$LOG_FILE"
  echo "$TS,$LABEL,$USER_INPUT" >> "$LOG_FILE"

  CONFIRM="Thank you. Your ${LABEL} has been recorded."
  echo "$CONFIRM"
  if command -v espeak >/dev/null 2>&1; then
    espeak "$CONFIRM"
  elif command -v say >/dev/null 2>&1; then
    say "$CONFIRM"
  fi
  exit 0
else
  ERR="Sorry, that is not a valid number. Please run the script again."
  echo "$ERR"
  if command -v espeak >/dev/null 2>&1; then
    espeak "$ERR"
  elif command -v say >/dev/null 2>&1; then
    say "$ERR"
  fi
  exit 1
fi
