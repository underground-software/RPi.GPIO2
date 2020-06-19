#!/bin/python3
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 0.5)
pwm.start(50)

time.sleep(10)

for i in range(20):
    pwm.ChangeFrequency(2 ** i)
    print("set frequency to", 2 ** i)
    time.sleep(3)

pwm.stop()
