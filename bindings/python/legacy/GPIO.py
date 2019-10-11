import gpiod

class GPIO:

    lines = {}

    BCM="gpiochip0"

    OUT=gpiod.LINE_REQ_DIR_OUT

    init = 0

    HIGH=1
    LOW=0

    @classmethod
    def setmode(cls, mode):
        if mode != cls.BCM:
            raise TypeError("Unknown GPIO mode")
        if cls.init == 0:
            cls.chip = gpiod.Chip(mode)
            cls.mode = mode
            cls.init = 1
        return

    @classmethod
    def setwarnings(cls, setting):
        pass

    @classmethod
    def setup(cls, pin, pinmode):
        if pinmode != cls.OUT:
            raise TypeError("Unknown pinmode") 
        cls.lines[pin] = cls.chip.get_line(pin)
        cls.lines[pin].request(consumer=cls.mode, type=pinmode)

    @classmethod
    def output(cls, pin, setting):
        cls.lines[pin].set_value(setting)

