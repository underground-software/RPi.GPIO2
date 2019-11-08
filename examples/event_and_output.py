#!/bin/env python3
import context
import gpiod
import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

GPIO._State.lines[25] = GPIO._State.chip.get_line(25)

GPIO._State.lines[25].request(consumer="./asasdf", type=gpiod.LINE_REQ_DIR_OUT)
# GPIO._State.lines[25].request(consumer="./asasdf", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
