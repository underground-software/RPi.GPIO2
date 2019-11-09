#!/bin/python3
import gpiod
from warnings import warn

chip = gpiod.Chip("gpiochip0")

line = chip.get_line(18)

print("chip:", chip.name(), "line:", line)

line.request(consumer=chip.name(), type=gpiod.LINE_REQ_DIR_IN)


line = chip.get_line(18)

x = [line]

for y in x:
    try:
        y.request(consumer=chip.name(), type=gpiod.LINE_REQ_DIR_OUT)
        y.set_value(1)
    except OSError:
        warn("there is a problem")


