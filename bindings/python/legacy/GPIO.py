import gpiod
from warnings import warn
import os
import sys
import time
from threading import Thread, Event

 # _            _       
# | |_ ___   __| | ___  
# | __/ _ \ / _` |/ _ \ 
# | || (_) | (_| | (_) |
 # \__\___/ \__,_|\___/ 

 # BIG TODO FIXME TODO FIXME implement BOARD MODE

# === User Facing Data ===


pin_to_gpio_rev3 = [
                    -1, -1, -1,  2, -1, 3,  -1,  4, 14, -1,
                    15, 17, 18, 27, -1, 22, 23, -1, 24, 10,
                    -1,  9, 25, 11,  8, -1,  7, -1, -1,  5,
                    -1,  6, 12, 13, -1, 19, 16, 26, 20, -1, 21
                   ]

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

# === Internal Data ===

# Internal library state
class _State:
    mode       = 0
    warnings   = True
    debuginfo  = True
    chip       = None
    event_ls   = []
    lines      = {}
    threads    = {}
    callbacks  = {}
    killsigs   = {}
    timestamps = {}

# Internal libgpiod constants
_OUTPUT = gpiod.Line.DIRECTION_OUTPUT
_INPUT = gpiod.Line.DIRECTION_INPUT

# === Helper Routines ===

def Dprint(*msgargs):
    """ Print debug information for development purposes"""
    if _State.debuginfo:
        print("[DEBUG]", *msgargs)

## Fuse these functions and refactor later *?*

def is_all_ints(data):
    if not is_iterable(data):
            data = [data]
    if len(data) < 1:
        return False
    return all([isinstance(elem,int) for elem in data]) \
        if not isinstance(data,int)\
            else True

def is_all_bools(data):
    if not is_iterable(data):
            data = [data]
    if len(data) < 1:
        return False
    return all([isinstance(elem,bool) for elem in data]) \
        if not isinstance(data,bool)\
            else True

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
    
    if direction == IN and initial:
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
            if initial is not None:
                    _State.lines[pin].set_value(initial)
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


def wait_for_edge(channel, edge, bouncetime=None, timeout=0):
    """
    Wait for an edge.  Returns the channel number or None on timeout.
    channel      - either board pin number or BCM number depending on which mode is set.
    edge         - RISING, FALLING or BOTH
    [bouncetime] - time allowed between calls to allow for switchbounce
    [timeout]    - timeout in ms

    {compat} bouncetime units are in seconds
    """

    # Running this function before setup is allowed but the initial pin value is undefined
    if channel not in _State.lines.keys():
        _State.lines[channel] = _State.chip.get_line(channel)

    if edge != RISING_EDGE and edge != FALLING_EDGE and edge != BOTH_EDGE:
        raise ValueError("The edge must be set to RISING, FALLING or BOTH")

    if bouncetime and bouncetime <= 0:
        raise ValueError("Bouncetime must be greater than 0") 

    if timeout and timeout < 0:
        raise ValueError("Timeout must be greater than or equal to 0") # error semantics differ from RPi.GPIO

    if _State.lines[channel].is_used() and not channel in _State.lines.keys():
        raise RuntimeError("Channel is currently in use (Device or Resource Busy)")
   #alt    PyErr_SetString(PyExc_RuntimeError, "Conflicting edge detection events already exist for this GPIO channel");
     
    if not _State.lines[channel].is_used():
        _State.lines[channel].request(consumer="GPIO666", type=edge)

    if timeout:
        timeout_sec = int(int(timeout) / 1000)
        timeout_nsec = (int(timeout) % 1000) * 1000
    else:
        timeout = 0

    if _State.lines[channel].event_wait(sec=timeout_sec, nsec=timeout_nsec):
        # We only care about bouncetime if it is explicitly speficied in the call to this function or if
        # this is not the first call to wait_for_edge on the specified pin
        if bouncetime and channel in _State.timestamps.keys():
            while 1:
                if time.time() - _State.timestamps[channel] > bouncetime:
                    break       # wait for $bouncetime to elapse before continuing
        _State.timestamps[channel] = time.time()
        _State.event_ls.append(channel)
        event = _State.lines[channel].event_read()

        # A hack to clear the event buffer by reading a bunch of bytes from the file representing the GPIO line
        eventfd = _State.lines[channel].event_get_fd()
        os.read(eventfd, 10000)
        return event
    else:
        return None

def poll_thread(channel, edge, callback, bouncetime):

    while not _State.killsigs[channel].is_set():
        if wait_for_edge(channel, edge, bouncetime, 1000):
            for callback_func in _State.callbacks[channel]:
                callback_func(channel)

def validate_pin_or_die(channel):
    if channel < 0 or channel > _State.chip.num_lines() - 1:
        raise ValueError("Invalid pin number")


def add_event_detect(channel, edge, callback=None, bouncetime=None):
    """
    Enable edge detection events for a particular GPIO channel.
    channel      - either board pin number or BCM number depending on which mode is set.
    edge         - RISING, FALLING or BOTH
    [callback]   - A callback function for the event (optional)
    [bouncetime] - Switch bounce timeout in ms for callback

    {compat} we do not require that the channel be setup as an input as a prerequiste to running this function,
    however the initial value on the channel is undefined
    """

    valid_edges = [RISING_EDGE, FALLING_EDGE, BOTH_EDGE]
    if edge not in valid_edges:
        raise ValueError("The edge must be set to RISING, FALLING or BOTH")

    if callback and not callable(callback):
        raise TypeError("Parameter must be callable")

    if bouncetime and bouncetime <= 0:
        raise ValueError ("Bouncetime must be greater than 0")

    validate_pin_or_die(channel)

    _State.threads[channel] = Thread(target=poll_thread, args=(channel, edge, callback, bouncetime))
    _State.callbacks[channel] = []

    if callback:
        _State.callbacks[channel].append(callback)

    _State.killsigs[channel] = Event()
    _State.threads[channel].start()


def add_event_callback(channel, callback):
    """
    Add a callback for an event already defined using add_event_detect()
    channel      - either board pin number or BCM number depending on which mode is set.
    callback     - a callback function"

    {compat} we do not require that the channel be setup as an input
    """

    if channel not in _State.threads.keys():
        raise RuntimeError("Add event detection using add_event_detect first before adding a callback")

    if not callable(callback):
        raise TypeError("Parameter must be callable")
    

    _State.callbacks[channel].append(callback)


def remove_event_detect(channel):
    """
    Remove edge detection for a particular GPIO channel
    channel - either board pin number or BCM number depending on which mode is set.
    """

    if channel in _State.threads.keys():
        _State.killsigs[channel].set()
        _State.threads[channel].join()
        del _State.threads[channel]
        del _State.killsigs[channel]
        del _State.callbacks[channel]
    else:
        raise ValueError("event detection not setup on channel {}".format(channel))


def event_detected(channel):
    """
    Returns True if an edge has occurred on a given GPIO.  You need to enable edge detection using add_event_detect() first.
    channel - either board pin number or BCM number depending on which mode is set."
    """

    if channel in _State.event_ls:
        _State.event_ls.remove(channel)
        return True
    else:
        return False


def cleanup():
    """
    Clean up by resetting all GPIO channels that have been used by this program to INPUT with no pullup/pulldown and no event detection
    [channel] - individual channel or list/tuple of channels to clean up.
    Default - clean every channel that has been used.

    {compat} Cleanup is handled by libgpiod and the kernel
    """

    for channel in _State.killsigs:
        _State.killsigs[channel].set()


def get_gpio_number(channel):
    if _State.mode == BOARD:
        if pin_to_gpio_rev3[channel] == -1:
            raise ValueError("The channel sent is invalid on a Raspberry Pi")
        else:
            return pin_to_gpio_rev3[channel]
    else:
        validate_pin_or_die(channel) 
        return channel


def gpio_function(channel):
    """
    Return the current GPIO function (IN, OUT, PWM, SERIAL, I2C, SPI)
    channel - either board pin number or BCM number depending on which mode is set.

    {compat} This is a stateless function that will return a constant value for every pin
    """

    # error handling is done in the called function
    return get_gpio_number(channel)
