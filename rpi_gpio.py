import bindings.python.legacy.GPIO as GPIO
#import gpiod.legacy.GPIO as GPIO

# important: https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering

import time

# GPIO.setdebuginfo(True)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
print("LED ON")
GPIO.output(18, GPIO.HIGH)
input()
time.sleep(1)
print("LED OFF")
GPIO.output(18, GPIO.LOW)
