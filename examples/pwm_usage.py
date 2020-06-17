#!/bin/python3
# PWM examples from Ben Croston
# source: https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
channel = 11
frequency = 10
freq = 100
dc = 20

GPIO.setup(11, GPIO.OUT)

p = GPIO.PWM(channel, frequency)

p.start(dc)   # where dc is the duty cycle (0.0 <= dc <= 100.0)

p.ChangeFrequency(freq)   # where freq is the new frequency in Hz

dc = 30
p.ChangeDutyCycle(dc)  # where 0.0 <= dc <= 100.0

p.stop()

GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 0.5)
p.start(1)
input('Press return to stop:')   # use raw_input for Python 2
p.stop()
GPIO.cleanup()
