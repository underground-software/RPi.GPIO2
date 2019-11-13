#!/bin/env python3
import context
import RPi.GPIO as GPIO

#GPIO.setup(25, GPIO.OUT)
#GPIO.setup(19, GPIO.IN)

#why doesn't it get seeet
# for i in range(1,26):
#     GPIO.setup(i,GPIO.IN)
#GPIO.output(25, GPIO.HIGH)

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

    # if not input_val:
        # print("button pressed")
        # GPIO.output(25,GPIO.LOW)
        # while not input_val:
        # input_val = GPIO.input(25)
        # GPIO.output(25,GPIO.HIGH)
