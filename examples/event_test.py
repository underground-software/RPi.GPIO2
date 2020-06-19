#!/bin/python3
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# We can successfully setup event detection on a channel
# configured in either direction because we quietly
# change the line_mode of the channel behind the scenes.
# In this way, the semantics of this library transparently
# differs from RPi.GPIO in that we are more permissive.
# This example causes the original RPi.GPIO to complain.
# TODO: verify that claim ^^

GPIO.setup(25, GPIO.OUT)
GPIO.wait_for_edge(25, GPIO.FALLING)

GPIO.setup(22, GPIO.IN)
GPIO.wait_for_edge(22, GPIO.FALLING)
