#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, time, json, traceback, subprocess, queue, sys
from threading import Thread
from difflib import SequenceMatcher
from flask import Flask, request, redirect, Response

# ==================== STDOUT/ERR 编码兜底（防 UnicodeEncodeError） ====================
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ==================== 音频驱动与路径 ====================
# 如播放没声音，可将 "alsa" 改为 "pulse" 再启动：SDL_AUDIODRIVER=pulse python3 app.py
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")

BASE = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE, "songs")

# ==================== Pygame mixer ====================
import pygame

def init_mixer():
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, channels=2, buffer=512)
        print(f"[AUDIO] mixer={pygame.mixer.get_init()} driver={os.environ.get('SDL_AUDIODRIVER')}")
    except Exception as e:
        print("[AUDIO][INIT ERROR]", e)
        traceback.print_exc()

init_mixer()

def mixer_busy_safe():
    try:
        return bool(pygame.mixer.get_init()) and pygame.mixer.music.get_busy()
    except Exception as e:
        print("[AUDIO][BUSY ERROR]", e)
        return False

# ==================== TTS（espeak-ng） ====================
def speak_sync(text: str):
    if not text: return
    try:
        subprocess.run(["espeak-ng", "-a", "200", "-s", "165", "-v", "en", text], check=False)
    except Exception as e:
        print("[TTS ERROR]", e)

def speak_async(text: str):
    if not text: return
    try:
        subprocess.Popen(["espeak-ng", "-a", "200", "-s", "165", "-v", "en", text])
    except Exception as e:
        print("[TTS ASYNC ERROR]", e)

START_LINE = "Hello! Let's start the music guessing game!"
PROMPT_LINE = "Can you guess the song?"
RESET_LINE = "Game reset. Starting over."
WRONG_LINE = "Oops! That's not right. Try again!"

# ==================== Helpers ====================
def normalize(s: str) -> str:
    if not s: return ""
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

# ==================== 固定播放列表（三首歌） ====================
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
is_paused = False
is_stopped = False
score = 0
last_guess = ""
round_token = 0  # 防止并发串台：每播放一首自增

def current_song_path():
    global current_idx
    current_idx = max(0, min(current_idx, len(PLAYLIST) - 1))
    return PLAYLIST[current_idx]

def play_path(path):
    """播放歌曲，并启动自动“播完-提问-录音-判断”线程"""
    global round_token
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    print("[PLAY]", path, "busy:", mixer_busy_safe())

    round_token += 1
    token = round_token
    Thread(target=auto_after_play, args=(token,), daemon=True).start()

def pause():
    global is_paused
    is_paused = True
    pygame.mixer.music.pause()

def unpause():
    global is_paused
    is_paused = False
    pygame.mixer.music.unpause()

def stop():
    global is_stopped
    is_stopped = True
    pygame.mixer.music.stop()


# ==================== STT（Vosk） ====================
USE_STT = True
try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer

    # 可通过环境变量指定麦克风设备索引，例如：MIC_DEVICE_INDEX=0 python3 app.py
    mic_env = os.environ.get("MIC_DEVICE_INDEX")
    if mic_env and mic_env.strip().isdigit():
        sd.default.device = (int(mic_env), None)
        print("[STT] default input set to", sd.default.device)

except Exception as e:
    USE_STT = False
    print("[STT] unavailable:", e)

def transcribe_once(seconds: int = 4, samplerate: int = 16000, device=None) -> str:
    if not USE_STT: return ""
    global _vosk_model
    try:
        _ = _vosk_model
    except NameError:
        print("[STT] loading vosk model...")
        _vosk_model = Model(model_name="vosk-model-small-en-us-0.15")
    recog = KaldiRecognizer(_vosk_model, samplerate)
    q = queue.Queue()

    def cb(indata, frames, t, status):
        if status: print("[STT][status]", status)
        q.put(bytes(indata))

    print(f"[STT] recording {seconds}s… device={device}")
    text = ""
    try:
        import sounddevice as sd  # lazy import for safety
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
    except Exception as e:
        print("[STT][STREAM ERROR]", e)
        traceback.print_exc()
    print("[STT] transcript:", text)
    return text.strip()

# ==================== 自动流程：歌播完 -> 问 -> 录音 -> 判断 ====================
def auto_after_play(token):
    global last_guess, score, current_idx, USE_STT, round_token

    try:
        # 等当前歌曲播放结束或被新一轮打断
        while True:
            if token != round_token:
                print("[AUTO] token changed, abort this round.")
                return
            if is_stopped or is_paused:
                print("[AUTO] manually paused/stopped, abort this round.")
                return
            if not mixer_busy_safe():
                break
            time.sleep(0.1)

        # 提示音（同步 TTS，确保听见）
        speak_sync(PROMPT_LINE)

        # 定义一个安全的录音函数（可复用）
        def safe_listen(prompt=""):
            if prompt:
                speak_sync(prompt)
            if not USE_STT:
                return ""
            try:
                return transcribe_once(seconds=4, samplerate=16000, device=None) or ""
            except Exception as e:
                print("[STT][listen ERROR]", e)
                traceback.print_exc()
                return ""

        # 初次录音
        text = safe_listen()
        last_guess = text or "(empty)"

        # 获取目标信息
        path = current_song_path()
        target = TITLE.get(path)
        accepted = ACCEPT.get(target, set())

        def is_correct(t):
            if not t or not target:
                return False
            n = normalize(t)
            for v in accepted:
                if normalize(v) in n:
                    return True
            return similar(t, target) >= 0.72

        # ================= 主循环 =================
        attempts = 0
        ok = is_correct(text)

        while not ok and attempts < 2:  # 最多再问两次
            attempts += 1
            if token != round_token:  # 被新一轮打断时立即退出
                print("[AUTO] aborted due to token change.")
                return
            text = safe_listen("Can you guess again?")
            last_guess = text or "(empty)"
            ok = is_correct(text)

        # ================= 结果处理 =================
        if ok:
            score += 1
            msg = f"Yes! You got it right! The song is {target}."
            speak_sync(msg)
            est = min(3, 0.2 * len(msg.split()))  # 大约每个单词0.1秒
            time.sleep(est)
            current_idx = (current_idx + 1) % len(PLAYLIST)
            play_path(current_song_path())
        else:
            speak_async(f"Let's move on. The answer was {target}.")
            current_idx = (current_idx + 1) % len(PLAYLIST)
            play_path(current_song_path())

    except Exception as e:
        print("[AUTO][ERROR]", e)
        traceback.print_exc()



# ==================== Flask ====================
app = Flask(__name__)

@app.route("/")
def home():
    return redirect("/controller")

@app.route("/controller")
def controller():
    # 安全读取 busy 与当前歌曲名，避免 500
    try:
        busy = mixer_busy_safe()
    except Exception as e:
        print("[CONTROLLER][busy ERROR]", e)
        busy = False

    try:
        song = os.path.basename(current_song_path())
    except Exception as e:
        print("[CONTROLLER][song ERROR]", e)
        song = "(unknown)"

    html = f"""
    <!doctype html><meta charset="utf-8"><title>Music Guessing</title>
    <style>
      body{{font-family:system-ui,sans-serif;padding:24px}}
      .row{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}}
      button{{padding:8px 16px;font-size:16px;cursor:pointer}}
      .badge{{padding:2px 6px;border-radius:6px;background:#eef}}
      .mono{{font-family:monospace}}
    </style>
    <h1>Music Guessing Controller (Auto-guess Mode)</h1>
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
    </form>

    <p>After each song finishes, the robot will ask: <b>"Can you guess the song?"</b> and listen for 4 seconds automatically.</p>
    <p>If TTS is silent, ensure <code>espeak-ng</code> is installed. If playback is silent, try <code>SDL_AUDIODRIVER=pulse</code>.</p>
    """
    return Response(html, mimetype="text/html")

@app.route("/action", methods=["POST"])
def action():
    global current_idx, score, is_stopped, is_paused
    cmd = (request.form.get("cmd") or "").lower().strip()
    print("[ACTION]", cmd)
    try:
        if cmd in ("start", "play"):
            is_stopped = False
            is_paused = False
            speak_sync(START_LINE)
            play_path(current_song_path())

        elif cmd == "pause":
            pause()

        elif cmd == "unpause":
            unpause()

        elif cmd == "stop":
            stop()

        elif cmd == "next":
            is_stopped = False
            is_paused = False
            current_idx = (current_idx + 1) % len(PLAYLIST)
            play_path(current_song_path())

        elif cmd == "prev":
            is_stopped = False
            is_paused = False
            current_idx = (current_idx - 1) % len(PLAYLIST)
            play_path(current_song_path())

        elif cmd == "reset":
            stop()
            current_idx = 0
            score = 0
            speak_async(RESET_LINE)

        else:
            print("[ACTION] unknown:", cmd)

    except Exception as e:
        print("[ACTION ERROR]", e)
        traceback.print_exc()

    return redirect("/controller")

@app.route("/debug")
def debug():
    info = {
        "driver": os.environ.get("SDL_AUDIODRIVER"),
        "mixer": str(pygame.mixer.get_init()),
        "busy": mixer_busy_safe(),
        "current_idx": current_idx,
        "current_song": current_song_path(),
        "score": score,
        "last_guess": last_guess,
        "USE_STT": USE_STT,
    }
    return info, 200

# 可选：本地 STT 自测端点
@app.route("/stt_test", methods=["POST"])
def stt_test():
    try:
        text = transcribe_once(seconds=4) if USE_STT else ""
        return {"ok": True, "text": text}, 200
    except Exception as e:
        traceback.print_exc()
        return {"ok": False, "error": str(e)}, 500

if __name__ == "__main__":
    speak_async("Controller ready.")
    # 若你需要固定输入设备，可通过环境变量 MIC_DEVICE_INDEX=0 传入；
    # 或者直接在上面把 device=None 改成 device=0。
    app.run(host="0.0.0.0", port=5000, debug=False)
