import time
import sys
import qwiic
import qwiic_proximity
from adafruit_servokit import ServoKit
import pygame 
import board
import busio
from threading import Thread

# ---------------- Audio Setup ----------------
pygame.mixer.init(frequency=44100, channels=2, buffer=512)
print("Audio system ready\n")

# ---------------- Music Files ----------------
MUSIC_FILES = [
    "music/music1.WAV",
    "music/music2.WAV",
    "music/music3.WAV",
    "music/music4.WAV",
    "music/music5.WAV",
    "music/music6.WAV"
]
current_music_index = 0  # Start with first music file


# ---------------- Servo Setup ----------------
kit = ServoKit(channels=16)

# Define multiple servos on channels 0, 2, and 4
servos = [kit.servo[i] for i in [0, 2, 4]]
for s in servos:
    s.set_pulse_width_range(500, 2500)

# ---------------- VL53L1X Distance Sensor Setup ----------------
print("VL53L1X Qwiic Test\n")
ToF = qwiic.QwiicVL53L1X(address=0x60)
if ToF.sensor_init() is None:
    print("VL53L1X Sensor online!\n")
else:
    print("Error initializing VL53L1X")

# ---------------- Proximity Sensor Setup ----------------
print("SparkFun Proximity Sensor VCN4040 Init\n")
oProx = qwiic_proximity.QwiicProximity()

if not oProx.connected:
    print("The Qwiic Proximity device isn't connected. Please check wiring.", file=sys.stderr)
    sys.exit(1)

oProx.begin()
print("Proximity Sensor online!\n")

# ---------------- Button Setup ----------------
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    BUTTON_AVAILABLE = True
    print("Button I2C initialized\n")
except Exception as e:
    BUTTON_AVAILABLE = False
    print(f"Button not available: {e}\n")

# ---------------- Button Monitor Function ----------------
def monitor_button():
    """Monitor button and change music selection"""
    global current_music_index
    
    if not BUTTON_AVAILABLE:
        print("Button monitoring disabled")
        return
    
    button_was_pressed = False
    while True:
        try:
            while not i2c.try_lock():
                time.sleep(0.01)
            
            # Read 4 bytes from button
            result = bytearray(4)
            i2c.readfrom_into(0x6f, result)
            i2c.unlock()
            
            # Check if button is pressed (byte[3] == 0x07)
            button_pressed = (result[3] == 0x07)
            
            # Detect button press (only when button goes from not pressed to pressed)
            if button_pressed and not button_was_pressed:
                current_music_index = (current_music_index + 1) % len(MUSIC_FILES)
                print(f"Button pressed! Switched to music {current_music_index + 1}: {MUSIC_FILES[current_music_index]}")
            
            button_was_pressed = button_pressed
            time.sleep(0.1)
        except Exception as e:
            print(f"Button error: {e}")
            try:
                i2c.unlock()
            except:
                pass
            time.sleep(0.5)

# ---------------- Start Button Thread ----------------
if BUTTON_AVAILABLE:
    button_thread = Thread(target=monitor_button, daemon=True)
    button_thread.start()
    print("Button monitoring started\n")



# ---------------- Main Loop ----------------
try:
    while True:
        # --- Read distance sensor ---
        ToF.start_ranging()
        time.sleep(0.005)
        distance = ToF.get_distance()  # in mm
        ToF.stop_ranging()

        # --- Read proximity sensor ---
        proxValue = oProx.get_proximity()

        # --- Convert and print readings ---
        distanceFeet = (distance / 25.4) / 12.0
        print(f"Distance(mm): {distance} | Distance(ft): {distanceFeet:.2f} | Proximity: {proxValue}")

        # --- Servo Control ---
        if proxValue > 560:
             # Play sound
            try:
                music_file = MUSIC_FILES[current_music_index]
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play()
                print(f"Playing {music_file}")
            except Exception as e:
                print(f"Error playing sound: {e}")
            time.sleep(1)
            # for s in servos:
            servos[0].angle = 180
            servos[1].angle = 0
        else:
            # for s in servos:
            servos[0].angle = 0
            servos[1].angle = 180

        time.sleep(0.4)

except KeyboardInterrupt:
    print("\nProgram stopped by user. Resetting servos...")
    for s in servos:
        s.angle = 0
    time.sleep(0.5)
    sys.exit(0)
