# Daniel's example (reproduced bug 6)
import RPi.GPIO as GPIO
import time
def callback_one(pin):
    print("CALLBACK")
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, GPIO.PUD_OFF)
GPIO.add_event_detect(21, GPIO.RISING, callback_one, 1)
input()
GPIO.cleanup()
