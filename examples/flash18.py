#!/bin/python3
import RPi.GPIO as GPIO
import RPi.GPIO_DEVEL as GPIO_DEVEL
import time

GPIO.setmode(GPIO.BCM)
GPIO_DEVEL.setdebuginfo(True)
GPIO.setup(18, GPIO.OUT)

for i in range(5):
    GPIO.output(18, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(18, GPIO.LOW)
    time.sleep(1)
