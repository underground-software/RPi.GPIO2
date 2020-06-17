#!/bin/python3
# Another example of PwM usage using the RPi.GPIO API
# By "alex"
# source: https://raspi.tv/2013/rpi-gpio-0-5-2a-now-has-software-pwm-how-to-use-it

# Don't try to run this as a script or it will all be over very quickly
# it won't do any harm though.
# these are all the elements you need to control PWM on 'normal' GPIO ports
# with RPi.GPIO - requires RPi.GPIO 0.5.2a or higher

# always needed with RPi.GPIO
import RPi.GPIO as GPIO


# choose BCM or BOARD numbering schemes. I use BCM
GPIO.setmode(GPIO.BCM)

# set GPIO 25 as an output. You can use any GPIO port
GPIO.setup(25, GPIO.OUT)

# create an object p for PWM on port 25 at 50 Hertz
# you can have more than one of these, but they need
# different names for each port
# e.g. p1, p2, motor, servo1 etc.
p = GPIO.PWM(25, 50)

# start the PWM on 50 percent duty cycle
# duty cycle value can be 0.0 to 100.0%, floats are OK
p.start(50)

# change the duty cycle to 90%
p.ChangeDutyCycle(90)

# change the frequency to 100 Hz (floats also work)
# e.g. 100.5, 5.2
p.ChangeFrequency(100)

# stop the PWM output
p.stop()

# when your program exits, tidy up after yourself
GPIO.cleanup()
