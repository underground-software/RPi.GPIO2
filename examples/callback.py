#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

testpin = 25


def callback_one(pin):
    print("CALLBACK FUNCTION NUMBER ONE")


def callback_two(pin):
    print("CALLBACK FUNCTION NUMBER TWO with lights")
    GPIO.output(18, 1)
    print("light callback over")
    print("CALLED:", callback_two.count)
    GPIO.output(18, 0)
    callback_two.count += 1


callback_two.count = 0


GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT, GPIO.PUD_OFF, 0)
GPIO.setup(25, GPIO.IN, GPIO.PUD_OFF)
GPIO.add_event_detect(testpin, GPIO.RISING, callback_one, 1)


print("ADD CALLBACK ONE")

input()

print("Event detected:", GPIO.event_detected(testpin))

print("ADD CALLBACK TWO")
GPIO.add_event_callback(testpin, callback_two)

input()

print("REMOVE EVENT DETECTION")

GPIO.remove_event_detect(25)

input()

print("ALL DONE")

GPIO.cleanup()
