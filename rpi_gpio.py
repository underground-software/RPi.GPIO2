from bindings.python.legacy.GPIO import GPIO
#import gpiod.legacy.GPIO as GPIO

import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(25, GPIO.OUT)
print("LED ON")
GPIO.output(25, GPIO.HIGH)
time.sleep(1)
print("LED OFF")
GPIO.output(25, GPIO.LOW)
