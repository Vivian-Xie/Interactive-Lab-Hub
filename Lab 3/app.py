import os, threading, time, queue, json
from flask import Flask, render_template, request, redirect, jsonify
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3
import pygame

# ==================== CONFIG ====================
AUDIO_SR = 16000
LISTEN_SECONDS = 5
CLIP_SECONDS = 8
LED_PIN = 22
BUTTON_PIN = 23
VOSK_MODEL_PATH = "/home/pi/vosk-model-small-en-us-0.15"  # 若无则用内置小模型
SONGS = [
    {"file": "songs/bad_guy.wav", "answers": ["bad guy", "billie eilish"]},
]
# ================================================

# -------- GPIO（可选）--------
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    def led_on(): GPIO.output(LED_PIN, 1)
    def led_off(): GPIO.output(LED_PIN, 0)
    def read_btn(): return GPIO.input(BUTTON_PIN)
except Exception as e:
    print("[WARN] GPIO not available:", e)
    def led_on(): pass
    def led_off(): pass
    def read_btn(): return 1

# -------- TTS --------
tts = pyttsx3.init()
def speak(text):
    try:
        print("[TTS]", text)
        tts.say(text); tts.runAndWait()
    except Exception as e:
        print("[TTS ERROR]", e)

# -------- 播放器（pygame）--------
pygame.mixer.init(frequency=AUDIO_SR, channels=1)
def play_clip(path, seconds=CLIP_SECONDS):
    try:
        if not os.path.exists(path):
            print("[AUDIO] missing:", path); return
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        t0 = time.time()
        while pygame.mixer.music.get_busy() and time.time()-t0 < seconds:
            time.sleep(0.05)
        pygame.mixer.music.stop()
    except Exception as e:
        print("[AUDIO ERROR]", e)

# -------- Vosk 识别 --------
def load_recognizer():
    print("[VOSK] Loading model...")
    if os.path.exists(VOSK_MODEL_PATH):
        model = Model(VOSK_MODEL_PATH)
    else:
        model = Model(lang="en-us")  # 首次联网会自动下载小模型
    return KaldiRecognizer(model, AUDIO_SR)

recognizer = load_recognizer()

def listen_once(sec=LISTEN_SECONDS):
    q = queue.Queue()
    def cb(indata, frames, t, status):
        if status: print(status)
        q.put(bytes(indata))
    text_final = ""
    recognizer.Reset()
    try:
        with sd.RawInputStream(samplerate=AUDIO_SR, blocksize=8000, dtype='int16',
                               channels=1, callback=cb):
            led_on()
            start = time.time()
            while time.time() - start < sec:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    chunk = res.get("text","").strip()
                    if chunk: text_final += " " + chunk
            res = json.loads(recognizer.FinalResult())
            fin = res.get("text","").strip()
            if fin: text_final += " " + fin
    except Exception as e:
        print("[LISTEN ERROR]", e)
    finally:
        led_off()
    return (text_final or "").strip().lower()

# -------- 游戏状态 --------
state = {"idx":0, "running":False, "last_heard":"", "last_result":"", "score":0}
state_lock = threading.Lock()

def button_thread():
    last = 1
    while True:
        try:
            cur = read_btn()
            if last == 1 and cur == 0:           # 按下沿
                with state_lock:
                    if not state["running"]:
                        state["running"] = True
                        speak("Game start")
                    else:
                        state["idx"] = (state["idx"] + 1) % max(1, len(SONGS))
                        speak("Next song")
            last = cur
            time.sleep(0.05)
        except Exception as e:
            print("[BUTTON ERROR]", e); time.sleep(0.5)

def game_loop():
    while True:
        with state_lock:
            running = state["running"]
            idx = state["idx"]
        if not running or not SONGS:
            time.sleep(0.2); continue

        song = SONGS[idx]
        speak("Listen")
        play_clip(song["file"])
        speak("Your guess?")
        heard = listen_once()
        print("[HEARD]", heard)
        with state_lock: state["last_heard"] = heard

        if not heard:
            speak("I didn't catch that")
            with state_lock: state["last_result"] = "no_input"
            continue

        ok = any(k in heard for k in song["answers"])
        if ok:
            speak("You got it")
            with state_lock:
                state["score"] += 1
                state["last_result"] = "correct"
                state["idx"] = (state["idx"] + 1) % max(1,len(SONGS))
        else:
            speak("Not quite, try again")
            with state_lock: state["last_result"] = "incorrect"
        time.sleep(0.3)

# -------- Flask 控制器 --------
app = Flask(__name__)

@app.route("/")
def home(): return redirect("/controller")

@app.route("/controller")
def controller():
    with state_lock:
        s = dict(state)
        if SONGS:
            s["current_file"] = SONGS[state["idx"]]["file"]
            s["answers"] = ", ".join(SONGS[state["idx"]]["answers"])
        else:
            s["current_file"] = "(no songs)"
            s["answers"] = ""
    return render_template("controller.html", s=s)

@app.route("/action", methods=["POST"])
def action():
    act = request.form.get("act","")
    with state_lock:
        if act == "start": state["running"] = True
        elif act == "pause": state["running"] = False
        elif act == "next": state["idx"] = (state["idx"] + 1) % max(1,len(SONGS))
        elif act == "reset": state.update({"idx":0,"running":False,"last_heard":"","last_result":"","score":0})
    return redirect("/controller")

@app.route("/state")
def api_state():
    with state_lock:
        s = dict(state)
        s["current_file"] = SONGS[state["idx"]]["file"] if SONGS else "(no songs)"
    return jsonify(s)

def start_threads():
    threading.Thread(target=button_thread, daemon=True).start()
    threading.Thread(target=game_loop, daemon=True).start()

if __name__ == "__main__":
    start_threads()
    app.run(host="0.0.0.0", port=5000, debug=False)
