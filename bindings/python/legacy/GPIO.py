import gpiod
from warnings import warn

class _State:
    mode = 0
    warnings = True
    debuginfo = True
    chip = None
    lines = {}


# Pin numbering modes
UNKNOWN =   0
BCM =       1
BOARD =     2

# Output modes
LOW =       0
HIGH =      1

# PUD modes
PUD_OFF =   0
PUD_UP =    1
PUD_DOWN =  2

# Data directions
IN = gpiod.LINE_REQ_DIR_IN
OUT = gpiod.LINE_REQ_DIR_OUT


def Dprint(*msgargs):
    """ Print debug information for development purposes"""
    if _State.debuginfo:
        print("[DEBUG]", *msgargs)


def setmode(mode):
    """
    Set up numbering mode to use for channels.
        BOARD - Use Raspberry Pi board numbers [unsupported]
        BCM   - Use Broadcom GPIO 00..nn numbers
    """
    if _State.mode != UNKNOWN:
        raise ValueError("A different mode has already been set!")

    if mode != BCM and mode != BOARD:
        raise ValueError("An invalid mode was passed to setmode()")

    # Temporarily:
    if mode == BOARD:
        raise ValueError("We currently do not suppprt BOARD mode")
    
    _State.mode = mode
    # This is hardcoded for now but that may change soon (or not)
    _State.chip = gpiod.Chip("gpiochip0")

    Dprint("mode set to", _State.mode)
    Dprint("state chip has value:", _State.chip)


def setwarnings(value):
    """Enable or disable warning messages"""
    _State.warnings = bool(value)
    Dprint("warning output set to", _State.warnings)

def setdebuginfo(value):
    """Enable or disable debug messages"""
    _State.debuginfo = bool(value)
    Dprint("debuginfo output set to", _State.debuginfo)


def is_all_ints(data):
    try:
        int(data)
    except TypeError:
        try:
            [ int(value) for value in data ]
        except ValueError:
            return False
        else:
            return True
    except ValueError:
        return False
    else:
        return True

# This function is pretty much pointless 
def is_all_bools(data):
    try:
        bool(data)
    except TypeError:
        try:
            [ bool(value) for value in data ]
        except ValueError:
            return False
        else:
            return True
    except ValueError:
        return False
    else:
        return True

def is_iterable(data):
    try:
        it = iter(data)
    except TypeError:
        return False
    else:
        return True

def setup(channel, direction, pull_up_down=PUD_OFF, initial=None):
    """
    Set up a GPIO channel or list of channels with a direction and (optional) pull/up down control
        channel        - either board pin number or BCM number depending on which mode is set.
        direction      - IN or OUT
        [pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN
        [initial]      - Initial value for an output channel
    """
    
    # Channel must contain only integral data
    if not is_all_ints(channel):
        raise ValueError("Channel must be an integer or list/tuple of integers")

    # Direction must be valid
    if direction != IN and direction != OUT:
        raise ValueError("An invalid direction was passed to setup()")

    if direction == OUT and pull_up_down != PUD_OFF:
        raise ValueError("pull_up_down parameter is not valid for outputs")
    
    if direction == IN and initial is not None:
        raise ValueError("initial parameter is not valid for inputs")

    if pull_up_down != PUD_OFF and pull_up_down != PUD_UP and pull_up_down != PUD_DOWN:
        raise ValueError("Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP or PUD_DOWN")

    # Make the channel data iterable by force
    if not is_iterable(channel):
        channel = [channel]
    
    for pin in channel:
        _State.lines[pin] = _State.chip.get_line(pin)
        try:
            _State.lines[pin].request(consumer=_State.chip.name(), type=direction)  
        except OSError:
            warn("This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.\n Further attemps to use this chip will fail unless setup() is run again sucessfully")
        
        
def output(channel, value):
    """
    Output to a GPIO channel or list of channel
    channel - either board pin number or BCM number depending on which mode is set.
    value   - 0/1 or False/True or LOW/HIGH
    """
    if not is_all_ints(channel):
        raise ValueError("Channel must be an integer or list/tuple of integers")

    if not is_iterable(channel):
       channel = [channel]

    if not is_all_ints(value) and not is_all_bools(value):
       raise ValueError("Value must be an integer/boolean or a list/tuple of integers/booleans")
    
    if not is_iterable(value):
        value = [value]

    if len(channel) != len(value):
       raise RuntimeError("Number of channel != number of value")

   
    for chan, val in zip(channel, value):
        if chan not in _State.lines.keys() or _State.lines[chan].direction() != gpiod.Line.DIRECTION_OUTPUT:
             warn("The GPIO channel has not been set up as an OUTPUT\n\tSkipping channel ", (chan))
        else:
            try:
                _State.lines[chan].set_value(bool(val))
            except PermissionError:
                warn("Unable to set value of channel {}, did you forget to run setup()? Or did setup() fail?".format(chan))
