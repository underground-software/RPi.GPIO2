import gpiod

MODE_OUT=gpiod.LINE_REQ_DIR_OUT

chip=gpiod.Chip("gpiochip0")

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
        self.line.request(consumer="gpiochip0", type=MODE_OUT)


pin = Pin(25, MODE_OUT)

pin.value = 1
input()
