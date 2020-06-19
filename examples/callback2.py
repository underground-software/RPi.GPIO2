#!/bin/python3
# Daniel's example (reproduced bug 6 until it was fixed)
import RPi.GPIO as GPIO
import time


def callback_one(pin):
    print("CALLBACK")


# Setup event detection on channel 21 for rising edge events
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, GPIO.PUD_OFF)
GPIO.add_event_detect(21, GPIO.RISING, callback_one, 1)

# Wait for user to press any key and then quit
input()
GPIO.cleanup()
