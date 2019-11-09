#!/bin/python3
import context
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(34, GPIO.IN)
GPIO.setup(34, GPIO.OUT)


    # with pytest.warns(Warning) as w:
    # assert "already in use" in str(w[0].message)


