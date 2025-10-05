#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob, traceback, threading, queue, subprocess
from flask import Flask, request, redirect, Response
import pygame

# ---------- Audio driver ----------
# If no sound, change "alsa" to "pulse" and restart Flask.
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")

# ---------- Paths ----------
BASE = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE, "songs")

# ---------- Mixer initialization ----------
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
    print("[TTS] pyttsx3 not available, will use espeak-ng fallback if present.")

_tts_q = queue.Queue()

def _tts_worker():
    if USE_PYTTSX3:
        eng = pyttsx3.init()
        try:
            eng.setProperty("rate", 165)
            # choose an English voice if available
            for v in eng.getProperty("voices"):
                if "en" in (v.id or "").lower():
                    eng.setProperty("voice", v.id)
                    break
        except Exception:
            pass
        while True:
            text = _tts_q.get()
            if text is None:
                break
            try:
                eng.say(text)
                eng.runAndWait()
            except Exception:
                traceback.print_exc()
    else:
        # fallback: espeak-ng
        while True:
            text = _tts_q.get()
            if text is None:
                break
            try:
                subprocess.run(["espeak-ng", text], check=False)
            except Exception:
                traceback.print_exc()

threading.Thread(target=_tts_worker, daemon=True).start()

def speak(text: str):
    if text:
        _tts_q.put(text)

# ---------- Script lines ----------
HOST_INTRO = (
    "Hi everyone! Meet our new interactive chatterbox. "
    "This box plays music and lets you guess songs while you wait in line. "
    "Let me show you how it works!"
)
ROBOT_INTRO = (
    "Hello! I am your chatterbox. I will play songs for you to guess. "
    "I will play the music until you guess it right or want to quit. "
    "Ready to start? Here we go!"
)
ROBOT_PROMPT = "Can you guess the song?"
CORRECT_TEMPLATE = "Yes! You got it right! The song is {title}. Here comes the next song!"
WRONG_TEMPLATE = "Oops! That's not right. Try again!"

# ---------- Playlist ----------
def scan_songs():
    patterns = [os.path.join(SONGS_DIR, "*.wav"), os.path.join(SONGS_DIR, "*.mp3")]
    files = []
    for p in patterns:
        files.extend(glob.glob(p))
    files = sorted(files)
    # prioritize bad_guy.wav if present
    bg = os.path.join(SONGS_DIR, "bad_guy.wav")
    if bg in files:
        files.remove(bg)
        files.insert(0, bg)
    return files

playlist = scan_songs()
current_idx = 0

def current_song():
    global current_idx
    if not playlist:
        return None
    current_idx = max(0, min(current_idx, len(playlist) - 1))
    return playlist[current_idx]

def reload_playlist_if_needed():
    global playlist, current_idx
    new_list = scan_songs()
    if new_list != playlist:
        playlist = new_list
        current_idx = 0
        print(f"[PLAYLIST] reloaded: {len(playlist)} file(s)")

# ---------- Playback control ----------
def play_path(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(path)
    print("[PLAY]", path)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    print("[PLAY] started; busy:", pygame.mixer.music.get_busy())

def pause():
    pygame.mixer.music.pause()

def unpause():
    pygame.mixer.music.unpause()

def stop():
    pygame.mixer.music.stop()

# ---------- Flask ----------
app = Flask(__name__)

# Speak host intro once at startup
speak(HOST_INTRO)

@app.route("/")
def home():
    return redirect("/controller")

@app.route("/controller")
def controller():
    reload_playlist_if_needed()
    busy = pygame.mixer.music.get_busy()
    vol = pygame.mixer.music.get_volume()
    song = current_song()
    song_name = os.path.basename(song) if song else "(no audio)"
    html = f"""
    <!doctype html><meta charset="utf-8"><title>Music Controller</title>
    <style>
      body {{ font-family: system-ui, sans-serif; padding: 24px; }}
      h1 {{ margin: 0 0 12px; }}
      .row {{ display:flex; gap:8px; margin:12px 0; flex-wrap: wrap; }}
      button {{ padding:8px 16px; font-size:16px; }}
      .info {{ margin-top:12px; color:#555; }}
      .badge {{ padding:2px 6px; border-radius:6px; background:#eef; }}
      .mono {{ font-family: monospace; }}
    </style>
    <h1>Music Guessing Controller</h1>
    <div class="info">
      <div>Driver: <span class="badge">{os.environ.get("SDL_AUDIODRIVER")}</span></div>
      <div>Mixer: <span class="badge">{pygame.mixer.get_init()}</span></div>
      <div>Status: <span class="badge">{'Playing' if busy else 'Idle'}</span></div>
      <div>Volume: <span class="badge">{vol:.2f}</span></div>
      <div>Song: <span class="mono">{song_name}</span></div>
      <div>Files in songs/: {len(playlist)}</div>
    </div>

    <form class="row" action="/action" method="post">
      <button type="submit" name="cmd" value="play">▶ Play</button>
      <button type="submit" name="cmd" value="pause">⏸ Pause</button>
      <button type="submit" name="cmd" value="unpause">⏯ Continue</button>
      <button type="submit" name="cmd" value="stop">⏹ Stop</button>
      <button type="submit" name="cmd" value="reset">🔁 Reset</button>
      <button type="submit" name="cmd" value="correct">✅ Correct</button>
      <button type="submit" name="cmd" value="wrong">❌ Wrong</button>
    </form>

    <p class="info">Tip: If you have no sound, edit app.py and change SDL_AUDIODRIVER to "pulse", then restart Flask.</p>
    """
    return Response(html, mimetype="text/html")

@app.route("/action", methods=["POST"])
def action():
    global current_idx
    cmd = (request.form.get("cmd") or "").lower().strip()
    print("[ACTION]", cmd)
    try:
        if cmd == "play":
            path = current_song()
            if path:
                speak(ROBOT_INTRO)
                play_path(path)
                speak(ROBOT_PROMPT)
            else:
                print("[ACTION] No audio found in", SONGS_DIR)

        elif cmd == "pause":
            pause()

        elif cmd == "unpause":
            unpause()

        elif cmd == "stop":
            stop()

        elif cmd == "reset":
            stop()
            current_idx = 0
            speak("Game reset. Starting over.")
            print("[RESET] current_idx=0")

        elif cmd == "next":
            if playlist:
                current_idx = (current_idx + 1) % len(playlist)
                play_path(current_song())
                speak("Next song. Can you guess the title?")

        elif cmd == "prev":
            if playlist:
                current_idx = (current_idx - 1) % len(playlist)
                play_path(current_song())
                speak("Previous song. Can you guess the title?")

        elif cmd == "correct":
            title = os.path.basename(current_song()) if current_song() else "the song"
            speak(CORRECT_TEMPLATE.format(title=title))
            if playlist:
                current_idx = (current_idx + 1) % len(playlist)
                play_path(current_song())
                speak(ROBOT_PROMPT)

        elif cmd == "wrong":
            speak(WRONG_TEMPLATE)

        else:
            print("[ACTION] unknown cmd:", cmd)

    except Exception as e:
        print("[ACTION ERROR]", e)
        traceback.print_exc()
    return redirect("/controller")

@app.route("/debug")
def debug():
    info = {
        "driver": os.environ.get("SDL_AUDIODRIVER"),
        "mixer": str(pygame.mixer.get_init()),
        "busy": pygame.mixer.music.get_busy(),
        "volume": pygame.mixer.music.get_volume(),
        "songs_dir": SONGS_DIR,
        "playlist_len": len(playlist),
        "current_idx": current_idx,
        "current_song": current_song(),
    }
    return info, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

