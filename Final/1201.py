###connected pi dist servo
import time
import sys
import random
import qwiic
import qwiic_proximity
import qwiic_gpio
from adafruit_servokit import ServoKit
import pygame 
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from threading import Thread

# ---------------- LED Setup ----------------
myGPIO = qwiic_gpio.QwiicGPIO()
if myGPIO.isConnected() == False:
    print("The Qwiic GPIO isn't connected to the system.", file=sys.stderr)
    sys.exit(1)
myGPIO.begin()
myGPIO.pinMode(2, myGPIO.GPIO_OUT)
myGPIO.pinMode(3, myGPIO.GPIO_OUT)
myGPIO.pinMode(1, myGPIO.GPIO_OUT)
myGPIO.pinMode(0, myGPIO.GPIO_OUT)
myGPIO.pinMode(4, myGPIO.GPIO_OUT)
print("LED initialized\n")

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
MYSTERIOUS_MUSIC = "music/mysterious.mp3"
current_music_index = 0

# ---------------- Servo Setup ----------------
kit = ServoKit(channels=16)
servos = [kit.servo[i] for i in [0, 2, 4, 6]]  # 4 servos
for s in servos:
    s.set_pulse_width_range(500, 2500)
    s.angle = 90  # Initialize all servos to stop

print("Servos initialized\n")

# ---------------- Display Setup ----------------
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

BAUDRATE = 64000000
spi = board.SPI()
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# ---------------- Backlight Setup ----------------
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# ---------------- Button Setup ----------------
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)

# ---------------- Image Setup ----------------
height = disp.width
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

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

# ---------------- State Variables ----------------
current_page = "insert_coin"  # "insert_coin", "ask_question", "home", "options", "selected"
last_buttonA_state = True
last_buttonB_state = True
selected_option = None  # Will store "random", "opt1", or "opt2"

# ---------------- Display Functions ----------------
def draw_insert_coin():
    """Draw Insert Coin page"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    draw.text((20, 60), "Insert Coin", font=font, fill=(255, 255, 0))
    disp.image(image, rotation)

def draw_ask_question():
    """Draw Ask Question page"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    
    # Title text
    draw.text((20, 10), "Think of your", font=font, fill=(200, 150, 255))
    draw.text((20, 35), "question...", font=font, fill=(200, 150, 255))
    
    # Box with ready button
    box_y = 70
    box_height = 50
    draw.rectangle((10, box_y, width-10, box_y+box_height), outline=(255,255,255), width=2)
    draw.text((15, box_y+15), "← Yes, I'm ready.", font=font, fill=(255, 255, 255))
    
    disp.image(image, rotation)

def draw_home_page():
    """Draw main page with Random and Pick one"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    
    # First box with "Random"
    box1_y = 10
    box1_height = 50
    draw.rectangle((10, box1_y, width-10, box1_y+box1_height), outline=(255,255,255), width=2)
    draw.text((20, box1_y+10), "Random Surprise", font=font, fill=(255, 255, 255))
    
    # Second box with "Pick one"
    box2_y = 70
    box2_height = 50
    draw.rectangle((10, box2_y, width-10, box2_y+box2_height), outline=(255,255,255), width=2)
    draw.text((20, box2_y+10), "Decide your own", font=font, fill=(255, 255, 255))
    
    disp.image(image, rotation)

def draw_options_page():
    """Draw options page with opt1 and opt2"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    
    box1_y = 10
    box1_height = 50
    draw.rectangle((10, box1_y, width-10, box1_y+box1_height), outline=(255,255,255), width=2)
    draw.text((20, box1_y+10), "Fate", font=font, fill=(255, 255, 255))
    
    # Second box with "Option2"
    box2_y = 70
    box2_height = 50
    draw.rectangle((10, box2_y, width-10, box2_y+box2_height), outline=(255,255,255), width=2)
    draw.text((20, box2_y+10), "Destiny", font=font, fill=(255, 255, 255))
    
    disp.image(image, rotation)

def draw_blank_page():
    """Draw blank black page"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    disp.image(image, rotation)

def play_mysterious_music():
    """Play mysterious background music"""
    try:
        pygame.mixer.music.load(MYSTERIOUS_MUSIC)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        print(f"Playing mysterious music...")
    except Exception as e:
        print(f"Error playing mysterious music: {e}")

def stop_music():
    """Stop currently playing music"""
    pygame.mixer.music.stop()
    print("Music stopped")

def blink_led_continuous():
    """Continuously blink LED in sequence 2-3-1-0-4"""
    pin_sequence = [2, 3, 1, 0, 4]
    for pin in pin_sequence:
        myGPIO.digitalWrite(pin, myGPIO.GPIO_HI)
        time.sleep(0.08)
        myGPIO.digitalWrite(pin, myGPIO.GPIO_LO)

def blink_led_fast():
    """Blink all LEDs together quickly"""
    print("LED blinking...")
    all_pins = [0, 1, 2, 3, 4]
    
    for i in range(5):  # Blink 5 times
        for pin in all_pins:
            myGPIO.digitalWrite(pin, myGPIO.GPIO_HI)
        time.sleep(0.1)
        for pin in all_pins:
            myGPIO.digitalWrite(pin, myGPIO.GPIO_LO)
        time.sleep(0.1)
    
    print("LED blink finished")
    
    # Make sure all LEDs are off at the end
    for pin in [0, 1, 2, 3, 4]:
        myGPIO.digitalWrite(pin, myGPIO.GPIO_LO)
    
    print("LED blink finished")
def play_music_and_spin_servos(servo_list):
    """Play music and spin selected servos for 1 second"""
    # Play music
    try:
        music_file = MUSIC_FILES[0]
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()
        print(f"Playing {music_file}")
        blink_led_fast() 
    except Exception as e:
        print(f"Error playing sound: {e}")
    
    # Start spinning servos
    for servo_index in servo_list:
        servos[servo_index].angle = 180
    print(f"Servos {servo_list} rotating...")
    
    # Rotate for 1 second
    time.sleep(0.1)
    
    # Stop servos
    for servo_index in servo_list:
        servos[servo_index].angle = 90
    print(f"Servos {servo_list} stopped")

# Show insert coin at start
draw_insert_coin()

# ---------------- Main Loop ----------------
try:
    while True:
        # --- Read proximity sensor ---
        proxValue = oProx.get_proximity()
        print(f"Proximity: {proxValue}")
        
        # Read button states (active LOW)
        buttonA_pressed = (buttonA.value == False)
        buttonB_pressed = (buttonB.value == False)
        
        # Detect button presses (rising edge)
        buttonA_just_pressed = buttonA_pressed and not last_buttonA_state
        buttonB_just_pressed = buttonB_pressed and not last_buttonB_state
        
        # --- Check if coin inserted (proximity > 156) ---
        if current_page == "insert_coin" and proxValue > 9000:
            # Play coin sound effect
            try:
                music_file = MUSIC_FILES[0]
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play()
                print(f"Playing inserting sound effect")
            except Exception as e:
                print(f"Error playing coin sound: {e}")
            
            time.sleep(1.5)  # Wait for coin sound to finish
            
            # Go to ask question page and play mysterious music
            current_page = "ask_question"
            draw_ask_question()
            play_mysterious_music()
            print("Coin detected! Showing ask question page")
        
        # --- Handle ask_question page ---
        elif current_page == "ask_question":
            # Button B moves to home page and stops music
            blink_led_continuous()
            if buttonB_just_pressed:
                stop_music()
                current_page = "home"
                draw_home_page()
                print("Ready! Showing home page")
        
        # --- Handle buttons based on current page ---
        elif current_page == "home":
            # Home page: A=random, B=go to options
            blink_led_continuous()
            if buttonA_just_pressed:
                selected_option = "random"
                current_page = "selected"
                draw_blank_page()
                print("Selected: Random")
                # Play music and spin servos 0 and 1
                play_music_and_spin_servos([0, 1])
                # Return to insert coin
                current_page = "insert_coin"
                draw_insert_coin()
            
            if buttonB_just_pressed:
                current_page = "options"
                draw_options_page()
                print("Showing options page")
        
        elif current_page == "options":
            # Options page: A=opt1, B=opt2
            blink_led_continuous()
            if buttonA_just_pressed:
                selected_option = "opt1"
                current_page = "selected"
                draw_blank_page()
                print("Selected: opt1")

                # Play music and spin servos 0 and 1
                play_music_and_spin_servos([0, 1])
                # Return to insert coin
                current_page = "insert_coin"
                draw_insert_coin()
            
            if buttonB_just_pressed:
                selected_option = "opt2"
                current_page = "selected"
                draw_blank_page()
                print("Selected: opt2")
                # Play music and spin servos 2 and 3
                play_music_and_spin_servos([2, 3])
                # Return to insert coin
                current_page = "insert_coin"
                draw_insert_coin()
        
        # Save button states
        last_buttonA_state = buttonA_pressed
        last_buttonB_state = buttonB_pressed
        
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\nProgram stopped by user. Resetting servos...")
    stop_music()
    for s in servos:
        s.angle = 90
    time.sleep(0.3)
    sys.exit(0)