#!/bin/python3
import GPIO
import time

def callback_one(pin):
    print("CALLBACK FUNCTION NUMBER ONE")

def callback_two(pin):
    print("CALLBACK FUNCTION NUMBER TWO")

GPIO.setmode(GPIO.BCM)
# GPIO.wait_for_edge(25, GPIO.BOTH_EDGE, 2000, 66660)
# print("pass1")
# GPIO.wait_for_edge(25, GPIO.BOTH_EDGE, 2000, 66660)
# print("pass2")
GPIO.add_event_detect(25, GPIO.BOTH_EDGE, callback_one, 666)

print("ADD CALLBACK ONE")

input()

print("Event detected:", GPIO.event_detected(25))

print("ADD CALLBACK TWO")
GPIO.add_event_callback(25, callback_two)

input()

print("ALL DONE")

GPIO.cleanup()
