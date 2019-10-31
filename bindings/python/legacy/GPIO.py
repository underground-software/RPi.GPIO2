import gpiod
from warnings import warn
import os
import sys
from multiprocessing import Process

class _State:
    mode      = 0
    warnings  = True
    debuginfo = True
    chip      = None
    lines     = {}
    _State.threads   = {}

# === User Facing Data ===

# Pin numbering modes
UNKNOWN = 0
BCM     = 1
BOARD   = 2

# Output modes
LOW  = 0
HIGH = 1

# PUD modes
PUD_OFF  = 0
PUD_UP   = 1
PUD_DOWN = 2

# Data directions
IN  = gpiod.LINE_REQ_DIR_IN
OUT = gpiod.LINE_REQ_DIR_OUT

# Request types
FALLING_EDGE    = gpiod.LINE_REQ_EV_FALLING_EDGE
RISING_EDGE     = gpiod.LINE_REQ_EV_RISING_EDGE
BOTH_EDGE       = gpiod.LINE_REQ_EV_BOTH_EDGES
AS_IS           = gpiod.LINE_REQ_DIR_AS_IS

# Event signal types
# NO_EDGE      = 0
# RISING_EDGE  = 1
# FALLING_EDGE = 2
# BOTH_EDGE    = 3

# === Internal Data ===

# Internal library state
class _State:
    mode      = 0
    warnings  = True
    debuginfo = False
    chip      = None
    lines     = {}

# Internal libgpiod constants
_OUTPUT = gpiod.Line.DIRECTION_OUTPUT
_INPUT = gpiod.Line.DIRECTION_INPUT

# === Helper Routines ===

def Dprint(*msgargs):
    """ Print debug information for development purposes"""
    if _State.debuginfo:
        print("[DEBUG]", *msgargs)

## Fuse these functions and refactor later

def is_all_ints(data):
    return all([isinstance(elem,int) for elem in data]) \
        if not isinstance(data,int)\
            else True

def is_all_bools(data):
    return all([isinstance(elem,bool) for elem in data]) \
        if not isinstance(data,bool)\
            else True

## Fuse these functions and refactor later

def is_iterable(data):
    try:
        it = iter(data)
    except TypeError:
        return False
    else:
        return True

# === Interface Functions ===

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
    
    # TODO: we should discuss this
    if mode == BCM:
        gpiochips = []
        for root, dirs, files in os.walk('/dev/'):
            for filename in files:
                if filename.find('gpio') > -1:
                    gpiochips.append(filename)
        if not gpiochips:
            raise ValueError("No compatible chips found")
    
    _State.mode = mode
    # This is hardcoded for now but that may change soon (or not)
    try:
        _State.chip = gpiod.Chip("gpiochip0")
    except PermissionError:
        print("Script or interpreter must be run as root")
        sys.exit()

    Dprint("mode set to", _State.mode)
    Dprint("state chip has value:", _State.chip)


def setwarnings(value = True):
    """Enable or disable warning messages"""
    _State.warnings = bool(value)
    Dprint("warning output set to", _State.warnings)

def setdebuginfo(value):
    """Enable or disable debug messages"""
    _State.debuginfo = bool(value)
    Dprint("debuginfo output set to", _State.debuginfo)


## Fuse these functions and refactor later

def is_all_ints(data):
    return all([isinstance(elem,int) for elem in data])\
        if not isinstance(data,int)\
            else True

def is_all_bools(data):
    return all([isinstance(elem,bool) for elem in data])\
        if not isinstance(data,bool)\
            else True

## Fuse these functions and refactor later

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
        if chan not in _State.lines.keys() or _State.lines[chan].direction() != _OUTPUT:
             warn("The GPIO channel has not been set up as an OUTPUT\n\tSkipping channel ", (chan))
        else:
            try:
                _State.lines[chan].set_value(bool(val))
            except PermissionError:
                warn("Unable to set value of channel {}, did you forget to run setup()? Or did setup() fail?".format(chan))

# This function needs to be tested
def input(channel):
    """
    Input from a GPIO channel.  Returns HIGH=1=True or LOW=0=False
    # channel - either board pin number or BCM number depending on which mode is set.
    """
    if channel not in _State.lines.keys() or (_State.lines[channel].direction() != _INPUT \
            and _State.lines[channel].direction() != _OUTPUT):
        raise RuntimeError("You must setup() the GPIO channel first")

    return _State.lines[channel].get_value()


def getmode():
    """
    Get numbering mode used for channel numbers.
    Returns BOARD, BCM or None
    """

    return _State.mode if _State.mode else None

   # {"wait_for_edge", (PyCFunction)py_wait_for_edge, METH_VARARGS | METH_KEYWORDS, "Wait for an edge.  Returbns the channel number or None on timeout.\nchannel      - either board pin number or BCM number depending on which mode is set.\nedge         - RISING, FALLING or BOTH\n[bouncetime] - time allowed between calls to allow for switchbounce\n[timeout]    - timeout in ms"},

def poll_thread(channel):
    _State.threads[channel] = Process(target=wait_for_edge, args=(channel))
    for i in _State.threads.keys():
        _State.threads[i].start()


    for i in _State.threads.keys():
        _State.threads[i].join()

def add_edge_detect():
    

def wait_for_edge(channel, edge, bouncetime=None, timeout=0):
    """
    Wait for an edge.  Returns the channel number or None on timeout.
    channel      - either board pin number or BCM number depending on which mode is set.
    edge         - RISING, FALLING or BOTH
    [bouncetime] - time allowed between calls to allow for switchbounce
    [timeout]    - timeout in ms
    """

    # if channel not in _State.lines.keys() or _State.lines[channel].direction() != _INPUT:
    #     raise RuntimeError("You must setup() the GPIO channel first")

    # FIXME: becaus we don't need to run setup, we do need to ensure that we have the line object in the dictionary
    if channel not in _State.lines.keys():
        _State.lines[channel] = _State.chip.get_line(channel)


    if edge != RISING_EDGE and edge != FALLING_EDGE and edge != BOTH_EDGE:
        raise ValueError("The edge must be set to RISING, FALLING or BOTH")

    if bouncetime is not None and bouncetime <= 0:
        raise ValueError("Bouncetime must be greater than 0") 

    if timeout is not None and timeout < 0:
        raise ValueError("Timeout must be greater than or equal to 0") # error semantics differ from RPi.GPIO

    if _State.lines[channel].is_used():
        raise RuntimeError("Channel is currently in use (Device or Resource Busy)")
   #alt    PyErr_SetString(PyExc_RuntimeError, "Conflicting edge detection events already exist for this GPIO channel");
     
    _State.lines[channel].request(consumer="GPIO666", type=edge)

    # Handle timeout value
    if timeout is not None:
        timeout_sec = int(int(timeout) / 1000)
        timeout_nsec = (int(timeout) % 1000) * 1000
    else:
        timeout = 0


    # TODO handle bouncetime
    if _State.lines[channel].event_wait(sec=timeout_sec, nsec=timeout_nsec):
        return _State.lines[channel].event_read()
    else:
        return None
    

# TODO 
   # {"add_event_detect", (PyCFunction)py_add_event_detect, METH_VARARGS | METH_KEYWORDS, "Enable edge detection events for a particular GPIO channel.\nchannel      - either board pin number or BCM number depending on which mode is set.\nedge         - RISING, FALLING or BOTH\n[callback]   - A callback function for the event (optional)\n[bouncetime] - Switch bounce timeout in ms for callback"},
   # {"remove_event_detect", py_remove_event_detect, METH_VARARGS, "Remove edge detection for a particular GPIO channel\nchannel - either board pin number or BCM number depending on which mode is set."},
   # {"event_detected", py_event_detected, METH_VARARGS, "Returns True if an edge has occurred on a given GPIO.  You need to enable edge detection using add_event_detect() first.\nchannel - either board pin number or BCM number depending on which mode is set."},

   # {"add_event_callback", (PyCFunction)py_add_event_callback, METH_VARARGS | METH_KEYWORDS, "Add a callback for an event already defined using add_event_detect()\nchannel      - either board pin number or BCM number depending on which mode is set.\ncallback     - a callback function"},
   # {"wait_for_edge", (PyCFunction)py_wait_for_edge, METH_VARARGS | METH_KEYWORDS, "Wait for an edge.  Returns the channel number or None on timeout.\nchannel      - either board pin number or BCM number depending on which mode is set.\nedge         - RISING, FALLING or BOTH\n[bouncetime] - time allowed between calls to allow for switchbounce\n[timeout]    - timeout in ms"},

# Implementation specific
   # {"gpio_function", py_gpio_function, METH_VARARGS, "Return the current GPIO function (IN, OUT, PWM, SERIAL, I2C, SPI)\nchannel - either board pin number or BCM number depending on which mode is set."},
   # {"cleanup", (PyCFunction)py_cleanup, METH_VARARGS | METH_KEYWORDS, "Clean up by resetting all GPIO channels that have been used by this program to INPUT with no pullup/pulldown and no event detection\n[channel] - individual channel or list/tuple of channels to clean up.  Default - clean every channel that has been used."},
