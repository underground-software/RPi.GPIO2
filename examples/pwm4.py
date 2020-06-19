#!/bin/python3
# A random PwM script pulled from a comment section
# by "Nick" and improved by "AndrewS" (@lurch on GitHub)
# source: https://raspi.tv/2013/rpi-gpio-0-5-2a-now-has-software-pwm-how-to-use-it#comment-29887
# source: https://raspi.tv/2013/rpi-gpio-0-5-2a-now-has-software-pwm-how-to-use-it#comment-30520

import RPi.GPIO as GPIO
import time

# PWM frequency
HZ = 100
FADESPEED = 0.002

GPIO.setmode(GPIO.BCM)

gpioPinsList = [["r1", 18], ["g1", 23], ["b1", 25], ["r2", 17], ["g2", 22], ["b2", 24]]
gpioPinsObjs = []

# setup GPIO pins as outputs and create PWM objects for each
for i in range(len(gpioPinsList)):
    GPIO.setup(gpioPinsList[i][1], GPIO.OUT)
    gpioPinsObjs.append(GPIO.PWM(gpioPinsList[i][1], HZ))

try:
    for pinObj in gpioPinsObjs:
        pinObj.start(100)
        time.sleep(FADESPEED)
    while True:
        #fade in
        for i in range(101):
            for pinObj in gpioPinsObjs:
                pinObj.ChangeDutyCycle(0 + i)
        time.sleep(FADESPEED)

        #fade out
        for i in range(101):
            for pinObj in gpioPinsObjs:
                pinObj.ChangeDutyCycle(100 - i)
        time.sleep(FADESPEED)
except KeyboardInterrupt:
    GPIO.cleanup()
    pass
