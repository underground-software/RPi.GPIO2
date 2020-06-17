#!/bin/python3
# Random examples from Ben Croston
# source: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
import RPi.GPIO as GPIO
import RPi.GPIO_DEVEL as GPIO_DEVEL

GPIO.setmode(GPIO.BOARD)

GPIO_DEVEL.Reset()

GPIO.setmode(GPIO.BCM)

mode = GPIO.getmode()

print("Is mode BCM:", mode == GPIO.BCM)

GPIO.setwarnings(False)

channel = 18
GPIO.setup(channel, GPIO.IN)
GPIO.setup(channel, GPIO.OUT)
GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)

# add as many channels as you want!
# you can tuples instead i.e.:
# chan_list = (11,12)
chan_list = [11, 12]
GPIO.setup(chan_list, GPIO.OUT)

GPIO.setup(18, GPIO.OUT)

GPIO.input(channel)

chan_list = [11, 12]                             # also works with tuples
GPIO.output(chan_list, GPIO.LOW)                # sets all to GPIO.LOW
GPIO.output(chan_list, (GPIO.HIGH, GPIO.LOW))   # sets first HIGH and second LOW

GPIO.cleanup()

channel = 18
channel1 = 19
channel2 = 21

GPIO.cleanup(channel)
GPIO.cleanup((channel1, channel2))
GPIO.cleanup([channel1, channel2])

print("Some useful information:")
print("RPi.GPIO_INFO:", GPIO.RPI_INFO)
print("RPi.GPIO_INFO['P1_REVISION]':", GPIO.RPI_INFO['P1_REVISION'])
print("GPIO.RPI_REVISION", GPIO.RPI_REVISION)  # (deprecated)

print("RPi.GPIO.VERSION:", GPIO.VERSION)
