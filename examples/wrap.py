#!/bin/env python3

import gpiod
import os

OUT=gpiod.LINE_REQ_DIR_OUT

gpiochips = []
for root, dirs, files in os.walk('/dev/'):
    for filename in files:
        if filename.find('gpio') > -1:
            print(filename)
            gpiochips.append(filename)

chip=gpiod.Chip(gpiochips[1])
# Also see gpid.ChipIter
for chp in gpiod.ChipIter():
    print(chp.name(), chp.label())
    if chp.name() == chip:
        print(chp.label())


# Concept of a wrapper using libgpio
class Pin:
    # _value = -1

    @property
    def value(self):
        return self.line.get_value()
        # return str(self.pin) + "=" + str(self._value)

    @value.setter
    def value(self, new):
        print(new)
        if new != 0 and new != 1:
            raise ValueError("value of pin must be zero or one")
        self.line.set_value(new)


    def __init__(self, pin, mode):
        self.line = chip.get_line(pin)
        self.line.request(consumer=gpiochips[1], type=OUT)
    
    def toggle(self):
        self.value = 0 if self.value else 1

pin = Pin(25, MODE_OUT)

pin.value = 1
input()
