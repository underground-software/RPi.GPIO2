#!/bin/python3
import context
import bindings.python.legacy.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# FIXME: can't run setup
# GPIO.setup(25, GPIO.OUT)

# GPIO._State.lines[25] = GPIO._State.chip.get_line(25)

GPIO.wait_for_edge(25, GPIO.FALLING_EDGE)

print(GPIO._State.lines[25].direction())
