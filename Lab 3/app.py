#!/usr/bin/env python3

import os, re, time, json, traceback, subprocess, queue
from difflib import SequenceMatcher
from flask import Flask, request, redirect, Response
import pygame

# ============ Audio / Paths ============
# If music is silent, change "alsa" -> "pulse" and restart.
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")

BASE = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE, "songs")

# ============ Mixer ============
def init_mixer():
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, channels=2, buffer=512)
        print(f"[AUDIO] mixer={pygame.mixer.get_init()} driver={os.environ.get('SDL_AUDIODRIVER')}")
    except Exception as e:
        print("[AUDIO][INIT ERROR]", e)
        traceback.print_exc()

init_mixer()

# ============ TTS (force espeak-ng, synchronous by default) ============
def speak_sync(text: str):
    if not text: 
        return
    try:
        # -a volume, -s speed, -v voice language
        subprocess.run(["espeak-ng", "-a", "200", "-s", "165", "-v", "en", text], check=False)
    except Exception as e:
        print("[TTS ERROR]", e)

def speak_async(text: str):
    if not text:
        return
    try:
        subprocess.Popen(["espeak-ng", "-a", "200", "-s", "165", "-v", "en", text])
    except Exception as e:
        print("[TTS ASYNC ERROR]", e)

START_LINE = "Hello! Let's start the music guessing game!"
PROMPT_LINE = "Can you guess the song?"
NEXT_LINE = "Next song. Can you guess the title?"
PREV_LINE = "Previous song. Can you guess the title?"
RESET_LINE = "Game reset. Starting over."
WRONG_LINE = "Oops! That's not right. Try again!"

# ============ Helpers ============
def normalize(s: str) -> str:
    if not s: return ""
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

# ============ Fixed playlist (your three songs) ============
PLAYLIST = [
    os.path.join(SONGS_DIR, "bad_guy.wav"),
    os.path.join(SONGS_DIR, "love_me_like_you_do.wav"),
    os.path.join(SONGS_DIR, "shape_of_you.wav"),
]
TITLE = {
    PLAYLIST[0]: "bad guy",
    PLAYLIST[1]: "love me like you do",
    PLAYLIST[2]: "shape of you",
}
ACCEPT = {
    "bad guy": {"bad guy", "billie eilish bad guy", "badguy"},
    "love me like you do": {"love me like you do", "love me like u do"},
    "shape of you": {"shape of you", "ed sheeran shape of you", "shapeofyou"},
}

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
    # prompt after song starts (non-blocking)
    speak_async(PROMPT_LINE)

def pause(): pygame.mixer.music.pause()
def unpause(): pygame.mixer.music.unpause()
def stop(): pygame.mixer.music.stop()

# ============ STT (Vosk, 4s capture) ============
USE_STT = True
try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
except Exception as e:
    USE_STT = False
    print("[STT] unavailable:", e)

def transcribe_once(seconds: int = 4, samplerate: int = 16000, device=None) -> str:
    if not USE_STT: return ""
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

# ============ Flask ============
app = Flask(__name__)

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
      body{{font-family:system-ui,sans-serif;padding:24px}}
      .row{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}}
      button{{padding:8px 16px;font-size:16px}}
      .badge{{padding:2px 6px;border-radius:6px;background:#eef}}
      .mono{{font-family:monospace}}
    </style>
    <h1>Music Guessing Controller</h1>
    <div>Status: <span class="badge">{'Playing' if busy else 'Idle'}</span></div>
    <div>Song: <span class="mono">{song}</span></div>
    <div>Score: <span class="badge">{score}</span></div>
    <div>Last guess: <span class="mono">{last_guess}</span></div>
    <form class="row" action="/action" method="post">
      <button type="submit" name="cmd" value="start">▶ Start</button>
      <button type="submit" name="cmd" value="play">▶ Play</button>
      <button type="submit" name="cmd" value="pause">⏸ Pause</button>
      <button type="submit" name="cmd" value="unpause">⏯ Continue</button>
      <button type="submit" name="cmd" value="stop">⏹ Stop</button>
      <button type="submit" name="cmd" value="prev">⏮ Prev</button>
      <button type="submit" name="cmd" value="next">⏭ Next</button>
      <button type="submit" name="cmd" value="reset">🔁 Reset</button>
      <button type="submit" formaction="/guess" formmethod="post">🎤 Guess (4s)</button>
    </form>
    <p>If robot voice is silent, install espeak-ng and/or change SDL_AUDIODRIVER to "pulse" and restart.</p>
    """
    return Response(html, mimetype="text/html")

@app.route("/action", methods=["POST"])
def action():
    global current_idx, score
    cmd = (request.form.get("cmd") or "").lower().strip()
    print("[ACTION]", cmd)
    try:
        if cmd in ("start", "play"):
            # speak BEFORE playing (blocking so you hear it for sure)
            speak_sync(START_LINE)
            play_path(current_song_path())
        elif cmd == "pause": pause()
        elif cmd == "unpause": unpause()
        elif cmd == "stop": stop()
        elif cmd == "next":
            current_idx = (current_idx + 1) % len(PLAYLIST)
            play_path(current_song_path())
        elif cmd == "prev":
            current_idx = (current_idx - 1) % len(PLAYLIST)
            play_path(current_song_path())
        elif cmd == "reset":
            stop(); current_idx = 0; score = 0
            speak_async(RESET_LINE)
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
    target = TITLE[current_song_path()]
    ok = False

    if text:
        ntext = normalize(text)
        for variant in ACCEPT[target]:
            if normalize(variant) in ntext:
                ok = True; break
        if not ok and similar(text, target) >= 0.72:
            ok = True

    if ok:
        score += 1
        speak_async(f"Yes! You got it right! The song is {target}.")
        current_idx = (current_idx + 1) % len(PLAYLIST)
        play_path(current_song_path())
    else:
        speak_async(WRONG_LINE)
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
    # Small boot cue so you know TTS path works
    speak_async("Controller ready.")
    app.run(host="0.0.0.0", port=5000, debug=False)
