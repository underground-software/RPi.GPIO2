#!/bin/python3
# Output and gpio_function examples from Ben Croston
# source: https://sourceforge.net/p/raspberry-gpio-python/wiki/Outputs/
# source: https://sourceforge.net/p/raspberry-gpio-python/wiki/Checking%20function%20of%20GPIO%20channels/

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup((11, 12), GPIO.OUT)

GPIO.output(12, GPIO.HIGH)
# or
GPIO.output(12, 1)
# or
GPIO.output(12, True)

GPIO.output(12, GPIO.LOW)
# or
GPIO.output(12, 0)
# or
GPIO.output(12, False)


chan_list = (11, 12)
GPIO.output(chan_list, GPIO.LOW)  # all LOW
GPIO.output(chan_list, (GPIO.HIGH, GPIO.LOW))  # first LOW, second HIGH

GPIO.setup(11, GPIO.IN)
GPIO.output(12, not GPIO.input(11))

GPIO.cleanup(12)

func = GPIO.gpio_function(12)
print("is channel 12 GPIO.UNKNOWN?", func == GPIO.UNKNOWN)

print("is channel 12 GPIO.OUT?:", func == GPIO.OUT)

print("setting up channel 12 as output...")
GPIO.setup(12, GPIO.OUT)

func = GPIO.gpio_function(12)
print("is channel 12 GPIO.UNKNOWN?", func == GPIO.UNKNOWN)

print("is channel 12 GPIO.OUT?:", func == GPIO.OUT)

GPIO.cleanup()
