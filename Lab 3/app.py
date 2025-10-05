#!/usr/bin/env python3

import os, re, glob, time, json, traceback, threading, queue, subprocess
from difflib import SequenceMatcher
from flask import Flask, request, redirect, Response
import pygame

# ---------- Audio driver ----------
# If you get no sound, change "alsa" to "pulse" and restart.
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")

# ---------- Paths ----------
BASE = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE, "songs")

# ---------- Mixer init ----------
def init_mixer():
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, channels=2, buffer=512)
        print(f"[AUDIO] mixer={pygame.mixer.get_init()} driver={os.environ.get('SDL_AUDIODRIVER')}")
    except Exception as e:
        print("[AUDIO][INIT ERROR]", e)
        traceback.print_exc()

init_mixer()

# ---------- TTS (pyttsx3 -> espeak-ng fallback) ----------
USE_PYTTSX3 = True
try:
    import pyttsx3
except Exception:
    USE_PYTTSX3 = False
    print("[TTS] pyttsx3 not available, using espeak-ng fallback if present.")

_tts_q = queue.Queue()

def _tts_worker():
    if USE_PYTTSX3:
        eng = pyttsx3.init()
        try:
            eng.setProperty("rate", 165)
            for v in eng.getProperty("voices"):
                if "en" in (v.id or "").lower():
                    eng.setProperty("voice", v.id)
                    break
        except Exception:
            pass
        while True:
            text = _tts_q.get()
            if text is None: break
            try:
                eng.say(text); eng.runAndWait()
            except Exception:
                traceback.print_exc()
    else:
        while True:
            text = _tts_q.get()
            if text is None: break
            try:
                subprocess.run(["espeak-ng", "-a", "200", "-s", "165", "-v", "en", text], check=False)
            except Exception:
                traceback.print_exc()

threading.Thread(target=_tts_worker, daemon=True).start()

def speak(text: str):
    if text:
        _tts_q.put(text)

# ---------- Helpers ----------
def normalize(s: str) -> str:
    if not s: return ""
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

# ---------- Song list (fixed to your 3 files) ----------
PLAYLIST = [
    os.path.join(SONGS_DIR, "bad_guy.wav"),
    os.path.join(SONGS_DIR, "love_me_like_you_do.wav"),
    os.path.join(SONGS_DIR, "shape_of_you.wav"),
]

# Pretty titles for speech and matching
TITLE_BY_PATH = {
    PLAYLIST[0]: "bad guy",
    PLAYLIST[1]: "love me like you do",
    PLAYLIST[2]: "shape of you",
}

# Accept common variants per song
ACCEPT = {
    "bad guy": {"bad guy", "billie eilish bad guy", "badguy"},
    "love me like you do": {"love me like you do", "love me like u do"},
    "shape of you": {"shape of you", "ed sheeran shape of you", "shapeofyou"},
}

# ---------- Playback ----------
current_idx = 0
score = 0
last_guess = ""

def current_song_path():
    global current_idx
    current_idx = max(0, min(current_idx, len(PLAYLIST) - 1))
    return PLAYLIST[current_idx]

def play_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    print("[PLAY]", path, "busy:", pygame.mixer.music.get_busy())

def pause(): pygame.mixer.music.pause()
def unpause(): pygame.mixer.music.unpause()
def stop(): pygame.mixer.music.stop()

# ---------- STT (Vosk 4s capture) ----------
USE_STT = True
try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
except Exception as e:
    USE_STT = False
    print("[STT] sounddevice/vosk unavailable:", e)

def transcribe_once(seconds: int = 4, samplerate: int = 16000, device=None) -> str:
    if not USE_STT:
        return ""
    global _vosk_model
    try:
        _ = _vosk_model
    except NameError:
        print("[STT] loading vosk model…")
        _vosk_model = Model(model_name="vosk-model-small-en-us-0.15")
    recog = KaldiRecognizer(_vosk_model, samplerate)
    q = queue.Queue()

    def cb(indata, frames, t, status):
        if status: print("[STT][status]", status)
        q.put(bytes(indata))

    print(f"[STT] recording {seconds}s…")
    text = ""
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype="int16",
                           channels=1, callback=cb, device=device):
        start = time.time()
        while time.time() - start < seconds:
            data = q.get()
            if recog.AcceptWaveform(data):
                res = json.loads(recog.Result()).get("text", "")
                if res: text = res
        final = json.loads(recog.FinalResult()).get("text", "")
        if final: text = final
    print("[STT] transcript:", text)
    return text.strip()

# ---------- Flask app ----------
app = Flask(__name__)

ROBOT_START = "Hello! Let's start the music guessing game!"

@app.route("/")
def home():
    return redirect("/controller")

@app.route("/controller")
def controller():
    busy = pygame.mixer.music.get_busy()
    song = os.path.basename(current_song_path())
    html = f"""
    <!doctype html><meta charset="utf-8"><title>Music Guessing</title>
    <style>
      body{{font-family:system-ui,sans-serif;padding:24px}} .row{{display:flex;gap:8px;flex-wrap:wrap}}
      button{{padding:8px 16px;font-size:16px}} .badge{{padding:2px 6px;border-radius:6px;background:#eef}}
      .mono{{font-family:monospace}}
    </style>
    <h1>Music Guessing Controller</h1>
    <div>Now: <span class="badge">{'Playing' if busy else 'Idle'}</span></div>
    <div>Song file: <span class="mono">{song}</span></div>
    <div>Score: <span class="badge">{score}</span></div>
    <div>Last guess: <span class="mono">{last_guess}</span></div>
    <form class="row" action="/action" method="post" style="margin:12px 0">
      <button type="submit" name="cmd" value="start">▶ Start</button>
      <button type="submit" name="cmd" value="pause">⏸ Pause</button>
      <button type="submit" name="cmd" value="unpause">⏯ Continue</button>
      <button type="submit" name="cmd" value="stop">⏹ Stop</button>
      <button type="submit" name="cmd" value="prev">⏮ Prev</button>
      <button type="submit" name="cmd" value="next">⏭ Next</button>
      <button type="submit" name="cmd" value="reset">🔁 Reset</button>
      <button type="submit" formaction="/guess" formmethod="post">🎤 Guess (4s)</button>
    </form>
    <p>If robot voice is silent, switch SDL_AUDIODRIVER at top of app.py to "pulse" and restart.</p>
    """
    return Response(html, mimetype="text/html")

@app.route("/action", methods=["POST"])
def action():
    global current_idx, score
    cmd = (request.form.get("cmd") or "").lower()
    print("[ACTION]", cmd)
    try:
        if cmd == "start":
            speak(ROBOT_START)
            time.sleep(0.3)  # let TTS begin
            play_path(current_song_path())
            speak("Can you guess the song?")
        elif cmd == "pause": pause()
        elif cmd == "unpause": unpause()
        elif cmd == "stop": stop()
        elif cmd == "next":
            current_idx = (current_idx + 1) % len(PLAYLIST)
            play_path(current_song_path()); speak("Next song. Guess the title.")
        elif cmd == "prev":
            current_idx = (current_idx - 1) % len(PLAYLIST)
            play_path(current_song_path()); speak("Previous song. Guess the title.")
        elif cmd == "reset":
            stop(); current_idx = 0; score = 0
            speak("Game reset. Starting over.")
        else:
            print("[ACTION] unknown:", cmd)
    except Exception as e:
        print("[ACTION ERROR]", e); traceback.print_exc()
    return redirect("/controller")

@app.route("/guess", methods=["POST"])
def guess():
    global last_guess, score, current_idx
    text = transcribe_once(seconds=4) if USE_STT else ""
    last_guess = text or "(empty)"
    target = TITLE_BY_PATH[current_song_path()]
    ok = False

    if text:
        ntext = normalize(text)
        # direct hit by any accepted variant
        for var in ACCEPT[target]:
            if normalize(var) in ntext:
                ok = True; break
        # fuzzy fallback
        if not ok and similar(text, target) >= 0.72:
            ok = True

    if ok:
        score += 1
        speak(f"Yes! You got it right! The song is {target}.")
        current_idx = (current_idx + 1) % len(PLAYLIST)
        play_path(current_song_path())
        speak("Next song. Can you guess the title?")
    else:
        speak("Oops! That's not right. Try again.")
    return redirect("/controller")

@app.route("/debug")
def debug():
    info = {
        "driver": os.environ.get("SDL_AUDIODRIVER"),
        "mixer": str(pygame.mixer.get_init()),
        "busy": pygame.mixer.music.get_busy(),
        "current_idx": current_idx,
        "current_song": current_song_path(),
        "score": score,
        "last_guess": last_guess,
    }
    return info, 200

if __name__ == "__main__":
    # Optional: speak on boot so you know TTS works
    speak("Controller ready.")
    app.run(host="0.0.0.0", port=5000, debug=False)

