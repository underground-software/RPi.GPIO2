#!/bin/python3
import GPIO
import time

testpin=25

def callback_one(pin):
    print("CALLBACK FUNCTION NUMBER ONE")

def callback_two(pin):
    print("CALLBACK FUNCTION NUMBER TWO with lights")
    GPIO.output(18, 1)
    print("light callback over")
    GPIO.output(18, 0)



GPIO.setmode(GPIO.BCM)
# GPIO.wait_for_edge(testpin, GPIO.BOTH_EDGE, 2000, 66660)
# print("pass1")
# GPIO.wait_for_edge(testpin, GPIO.BOTH_EDGE, 2000, 66660)
# print("pass2")

GPIO.add_event_detect(testpin, GPIO.BOTH_EDGE, callback_one, 666)

GPIO.setup(18, GPIO.OUT, GPIO.PUD_OFF)

# GPIO.output(18, 0)

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
