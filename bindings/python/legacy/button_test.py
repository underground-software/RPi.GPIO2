#!/bin/env python3

import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(19, GPIO.IN)
GPIO.output(25, GPIO.HIGH)
while True:
    
    input_val = GPIO.input(19)
    if not input_val:
        print("button pressed")
        GPIO.output(25,GPIO.LOW)
        while not input_val:
            input_val = GPIO.input(19)
        GPIO.output(25,GPIO.HIGH)
