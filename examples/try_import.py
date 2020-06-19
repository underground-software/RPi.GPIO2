#!/bin/python3
# An example of how one may import this library
# by Ben Croston
# Source: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! \
    This is probably because you need superuser privileges. \
    You can achieve this by using 'sudo' to run your script")


# Note that one may use this library as a non-superuser
# by setting the Linux file group to a group such as gpi
# and adding a user to that group with a command
# like: `sudo usermod -aG gpio <user>`
