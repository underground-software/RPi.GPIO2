#!/bin/python3
# Input examples from Ben Croston
# source: https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

channel = 18

GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# or
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

if GPIO.input(channel):
    print('Input was HIGH')
else:
    print('Input was LOW')

# wait for button (real example doensn't have the "or False" at the end)
while GPIO.input(channel) == GPIO.LOW or False:
    time.sleep(0.01)  # wait 10 ms to give CPU chance to do other things


GPIO.wait_for_edge(channel, GPIO.RISING)

# wait for up to 5 seconds for a rising edge (timeout is in milliseconds)
channel = GPIO.wait_for_edge(channel, GPIO.RISING, timeout=5000)
if channel is None:
    print('Timeout occurred')
else:
    print('Edge detected on channel', channel)


def do_something():
    print("running do_something()")


channel = 18
GPIO.add_event_detect(channel, GPIO.RISING)  # add rising edge detection on a channel
do_something()
if GPIO.event_detected(channel):
    print('Button pressed')


def my_callback(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s' % channel)
    print('This is run in a different thread to your main program')


GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback)  # add rising edge detection on a channel
# ...the rest of your program...


def my_callback_one(channel):
    print('Callback one')


def my_callback_two(channel):
    print('Callback two')


GPIO.add_event_detect(channel, GPIO.RISING)
GPIO.add_event_callback(channel, my_callback_one)
GPIO.add_event_callback(channel, my_callback_two)

# add rising edge detection on a channel, ignoring further edges for 200ms for switch bounce handling
GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=200)

# This example is on the linked webpage but it is wrong, I checked the RPi.GPIO source code
# GPIO.add_event_callback(channel, my_callback, bouncetime=200)

GPIO.remove_event_detect(channel)
