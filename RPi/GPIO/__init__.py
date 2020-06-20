"""
The RPi.GPIO API
Originally created by Ben Croston
Reimplemented and extended by Joel Savitz and Fabrizio D'Angelo
This is free software, see LICENSE for details
"""

from RPi.core import\
    BCM,\
    BOARD,\
    BOTH,\
    FALLING,\
    HARD_PWM,\
    HIGH,\
    I2C,\
    IN,\
    LOW,\
    OUT,\
    PUD_DISABLE,\
    PUD_DOWN,\
    PUD_OFF,\
    PUD_UP,\
    PWM,\
    RISING,\
    RPI_INFO,\
    RPI_REVISION,\
    SERIAL,\
    SPI,\
    UNKNOWN,\
    VERSION,\
    add_event_callback,\
    add_event_detect,\
    channel_valid_or_die,\
    cleanup,\
    event_detected, \
    getactive_state,\
    getbias,\
    getdirection,\
    getmode,\
    gpio_function,\
    input,\
    output,\
    remove_event_detect,\
    setactive_state,\
    setbias,\
    setdirection,\
    setmode,\
    setup,\
    setwarnings,\
    wait_for_edge

# python3-libgpiod-rpi base version
VERSION2 = "0.3.0a3"  # Leviticus Alpha Trois
