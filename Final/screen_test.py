# button_display.py
import time
import random
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

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

# Load font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# ---------------- Page State ----------------
current_page = "home"  # "home", "options", "blank"
last_buttonA_state = True
last_buttonB_state = True

def draw_home_page():
    """Draw main page with Random and Pick one"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    
    # First box with "Random"
    box1_y = 30
    box1_height = 50
    draw.rectangle((10, box1_y, width-10, box1_y+box1_height), outline=(255,255,255), width=2)
    draw.text((20, box1_y+10), "Random", font=font, fill=(255, 255, 255))
    
    # Second box with "Pick one"
    box2_y = 100
    box2_height = 50
    draw.rectangle((10, box2_y, width-10, box2_y+box2_height), outline=(255,255,255), width=2)
    draw.text((20, box2_y+10), "Pick one", font=font, fill=(255, 255, 255))
    
    disp.image(image, rotation)

def draw_options_page():
    """Draw options page with opt1 and opt2"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    
    # First line: opt1
    draw.text((20, 30), "opt1", font=font, fill=(255, 255, 255))
    
    # Second line: opt2
    draw.text((20, 80), "opt2", font=font, fill=(255, 255, 255))
    
    disp.image(image, rotation)

def draw_blank_page():
    """Draw blank black page"""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    disp.image(image, rotation)

# Show home page at start
draw_home_page()

# ---------------- Main Loop ----------------
while True:
    # Read button states (active LOW)
    buttonA_pressed = (buttonA.value == False)
    buttonB_pressed = (buttonB.value == False)
    
    # Detect button A press (rising edge)
    buttonA_just_pressed = buttonA_pressed and not last_buttonA_state
    
    # Detect button B press (rising edge)
    buttonB_just_pressed = buttonB_pressed and not last_buttonB_state
    
    # Handle buttons based on current page
    if current_page == "home":
        # Home page: A=random, B=go to options
        if buttonA_just_pressed:
            random_num = random.randint(1, 100)
            print(f"Random: {random_num}")
        
        if buttonB_just_pressed:
            current_page = "options"
            draw_options_page()
    
    elif current_page == "options":
        # Options page: A or B both go to blank
        if buttonA_just_pressed or buttonB_just_pressed:
            current_page = "blank"
            draw_blank_page()
    
    elif current_page == "blank":
        # Blank page: A or B go back to home
        if buttonA_just_pressed or buttonB_just_pressed:
            current_page = "home"
            draw_home_page()
    
    # Save button states
    last_buttonA_state = buttonA_pressed
    last_buttonB_state = buttonB_pressed
    
    time.sleep(0.05)  # Small delay for button debounce