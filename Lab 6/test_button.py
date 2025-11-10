# qwiic_button_test.py  （适用于 Raspberry Pi 5）
import time
import board
import busio

ADDR = 0x6F
REG_STATUS = 0x03          # 按钮状态寄存器
MASK_PRESSED = 0x04        # bit2 = 当前是否按下

i2c = busio.I2C(board.SCL, board.SDA)

def read_reg(addr, nbytes=1):
    while not i2c.try_lock():
        pass
    try:
        # 先写寄存器地址，再读
        i2c.writeto(ADDR, bytes([addr]))
        buf = bytearray(nbytes)
        i2c.readfrom_into(ADDR, buf)
        return buf
    finally:
        i2c.unlock()

print("Ready. Press and release the Qwiic Button...")
last_pressed = None

try:
    while True:
        status = read_reg(REG_STATUS, 1)[0]
        pressed = (status & MASK_PRESSED) != 0
        if pressed != last_pressed:
            print("Button Pressed!" if pressed else "Button Released.")
            last_pressed = pressed
        time.sleep(0.02)  # 50Hz 轮询
except KeyboardInterrupt:
    pass
