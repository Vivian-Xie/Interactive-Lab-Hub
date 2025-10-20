# import time
# from adafruit_servokit import ServoKit

# # Set channels to the number of servo channels on your kit.
# # There are 16 channels on the PCA9685 chip.
# kit = ServoKit(channels=16)

# # Name and set up the servo according to the channel you are using.
# servo = kit.servo[0]

# # Set the pulse width range of your servo for PWM control of rotating 0-180 degree (min_pulse, max_pulse)
# # Each servo might be different, you can normally find this information in the servo datasheet
# servo.set_pulse_width_range(500, 2500)

# while True:
#     try:
        
#         # Set the servo to 180 degree position
#         servo.angle = 180
#         time.sleep(2)
#         # Set the servo to 0 degree position
#         servo.angle = 0
#         time.sleep(2)
        
#     except KeyboardInterrupt:
#         # Once interrupted, set the servo back to 0 degree position
#         servo.angle = 0
#         time.sleep(0.5)
#         break
import time
from adafruit_servokit import ServoKit

# 初始化 PCA9685 控制板（16 通道）
kit = ServoKit(channels=16)

# 舵机1接在接口0（第1个）
servo1 = kit.servo[0]
# 舵机2接在接口1（第2个）
servo2 = kit.servo[2]

# 设置每个舵机的脉宽范围（根据舵机型号微调）
servo1.set_pulse_width_range(500, 2500)
servo2.set_pulse_width_range(500, 2500)

try:
    while True:
        # 转到 180°
        servo1.angle = 180
        servo2.angle = 0
        time.sleep(2)

        # 转回 0°
        servo1.angle = 0
        servo2.angle = 180
        time.sleep(2)

except KeyboardInterrupt:
    # 终止时复位舵机位置
    servo1.angle = 0
    servo2.angle = 0
    time.sleep(0.5)
