#!/bin/env python3
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)
GPIO.setup(25, GPIO.IN)

prev = 0

print("GUITAR HERO LITE")

score = 0

while True:
    input_val = GPIO.input(25)
    if input_val > prev:
        print("Button pressed. Score:", score)
        score = score + 1
    elif input_val < prev:
        print("Button released")

    prev = input_val
