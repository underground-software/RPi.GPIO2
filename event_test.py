#!/bin/python3
import bindings.python.legacy.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(25, GPIO.IN)

GPIO._State.lines[25] = GPIO._State.chip.get_line(25)

GPIO.wait_for_edge(25, GPIO.FALLING_EDGE)
