#!/bin/python3
import context
import RPi.GPIO as GPIO

# This kills WiFi when pin=34
pin=18
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN)
