# qwiic_button_count_5s.py
# Device: SparkFun Qwiic Button (I2C address 0x6F)
# Flow: 3-second countdown -> 5-second measurement window -> count button presses
# Counts only on the "press" edge, includes light debounce.

import time
import board
import busio

ADDR = 0x6F
REG_STATUS = 0x03          # Button status register
MASK_PRESSED = 0x04        # bit2 = pressed when this bit is 1

POLL_INTERVAL = 0.01       # Check every 10ms (100Hz)
DEBOUNCE_SEC = 0.06        # 60ms debounce

i2c = busio.I2C(board.SCL, board.SDA)

def read_reg(addr, nbytes=1):
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(ADDR, bytes([addr]))
        buf = bytearray(nbytes)
        i2c.readfrom_into(ADDR, buf)
        return buf
    finally:
        i2c.unlock()

def is_pressed():
    status = read_reg(REG_STATUS, 1)[0]
    return (status & MASK_PRESSED) != 0

def main():
    print("Starting 3-second countdown...")
    for t in range(3, 0, -1):
        print(t)
        time.sleep(1)

    print("Go! You have 5 seconds. Press the button as many times as you can!")

    press_count = 0
    last_state = is_pressed()
    last_edge_time = 0.0
    start_time = time.time()

    while (time.time() - start_time) < 5.0:
        cur_state = is_pressed()
        now = time.time()

        # Count only the rising edge (not pressed -> pressed), debounce protected
        if (not last_state) and cur_state and (now - last_edge_time) >= DEBOUNCE_SEC:
            press_count += 1
            last_edge_time = now
            print(f"Press count: {press_count}")

        last_state = cur_state
        time.sleep(POLL_INTERVAL)

    print("Time's up!")
    print(f"Total presses in 5 seconds: {press_count}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted, exiting.")
