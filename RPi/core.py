"""
Core implementation of python3-libgpiod-rpi
By Joel Savitz and Fabrizio D'Angelo
This is free software, see LICENSE for details
"""

import gpiod
from warnings import warn
import os
import sys
import time
from threading import Thread, Event, Lock
import atexit

# BCM to Board mode conversion table for Raspbery Pi 3 Model B
pin_to_gpio_rev3 = [
                    -1, -1, -1,  2, -1, 3,  -1,  4, 14, -1,     # NOQA
                    15, 17, 18, 27, -1, 22, 23, -1, 24, 10,     # NOQA
                    -1,  9, 25, 11,  8, -1,  7, -1, -1,  5,     # NOQA
                    -1,  6, 12, 13, -1, 19, 16, 26, 20, -1, 21  # NOQA
                   ]


# === User Facing Data ===

# Exact values for constants taken from RPi.GPIO source code
# file: source/common.h

# [API] RPi.GPIO API version (not python3-libgpiod-rpi version)
# NOTE: we currently only officially support the Raspbery Pi 3 Model B
# but we soon plan to implement support for the Raspbery Pi 4 Model B
# We are limited by the hardware available to the developers
VERSION     = "0.7.0"

# [API] Hardware information
RPI_INFO    = {
    "P1_REVISION":      3,
    "REVISION":         "a22082",
    "TYPE":             "Pi 3 Model B",
    "MANUFACTURER":     "Embest"
    "PROCESSOR"         "BCM2837",
    "RAM":              "1G",
}
# [API] Depcrecated source of hardware information
RPI_REVISION = RPI_INFO["P1_REVISION"]

# [API] Pin numbering modes
UNKNOWN     = -1
BCM         = 11
BOARD       = 10

# [API] Random constants defined but unused in the latest RPi.GPIO release
SERIAL      = 40
SPI         = 41
I2C         = 42
HARD_PWM    = 43

# [API] Output modes
LOW  = gpiod.Line.ACTIVE_LOW
HIGH = gpiod.Line.ACTIVE_HIGH

_LINE_ACTIVE_STATE_COSNT_TO_FLAG = {
    LOW: gpiod.LINE_REQ_FLAG_ACTIVE_LOW,
    HIGH: 0,  # Active High is set by the default flag
}


# Macro
def active_flag(const):
    return _LINE_ACTIVE_STATE_COSNT_TO_FLAG[const]


# [API] Software pull up/pull down resistor modes
# We map RPi.GPIO PUD modes to libgpiod PUD constants
PUD_OFF     = gpiod.Line.BIAS_AS_IS
PUD_UP      = gpiod.Line.BIAS_PULL_UP
PUD_DOWN    = gpiod.Line.BIAS_PULL_DOWN

# We extend RPi.GPIO with the ability to explicitly disable pull up/down behavior
PUD_DISABLE = gpiod.Line.BIAS_DISABLE

# libgpiod uses distinct flag values for each line bias constant returned by
# the gpiod.Line.bias() method. To simplify our translation, we map the latter
# to the former with the following dictionary
_LINE_BIAS_CONST_TO_FLAG = {
    PUD_OFF:    0,  # This behavior is indicated with the default flag
    PUD_UP:     gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
    PUD_DOWN:   gpiod.LINE_REQ_FLAG_BIAS_PULL_DOWN,
    PUD_DISABLE: gpiod.LINE_REQ_FLAG_BIAS_DISABLE,
}


# Macro
def bias_flag(const):
    return _LINE_BIAS_CONST_TO_FLAG[const]


# Internal line modes
_line_mode_none     = 0
_line_mode_in       = gpiod.LINE_REQ_DIR_IN
_line_mode_out      = gpiod.LINE_REQ_DIR_OUT
_line_mode_falling  = gpiod.LINE_REQ_EV_FALLING_EDGE
_line_mode_rising   = gpiod.LINE_REQ_EV_RISING_EDGE
_line_mode_both     = gpiod.LINE_REQ_EV_BOTH_EDGES
# As of yet unused and unexposed
# TODO investigate AS_IS kernel behavior
_line_mode_as_is    = gpiod.LINE_REQ_DIR_AS_IS


# [API] Line event types
FALLING     = _line_mode_falling
RISING      = _line_mode_rising
BOTH        = _line_mode_both
# As of yet unused and unexposed
#AS_IS       = _line_mode_as_is

# NOTE: libgpiod also exposes enumerated direction constants seperate from the
# request constants, but the distinction is not relevant for our use case

# [API] Data direction types
IN  = _line_mode_in
OUT = _line_mode_out


# We map internal line modes to RPI.GPIO API direction constants for getdirection()
_LINE_MODE_TO_DIR_CONST = {
    _line_mode_none:    -1,
    _line_mode_in:      IN,
    _line_mode_out:     OUT,
    _line_mode_falling: IN,
    _line_mode_rising:  IN,
    _line_mode_both:    IN,
    # This mode is not used by any functionality and so an appearance of this value
    # signals something gone wrong in the library
    _line_mode_as_is:   -662,
}

# line thread types, these threads can be run on an individual line
_line_thread_none       = 0
_line_thread_poll       = 1 << 1
_line_thread_pwm        = 1 << 2

# === Internal Data ===


class _LineThread(Thread):
    def __init__(self, channel, target_type, args):
        target = _LINE_THREAD_TYPE_TO_TARGET[target_type]
        super().__init__(target=target, args=args)
        self.killswitch = Event()
        self.target_type = target_type
        self.channel = channel

    def kill(self):
        self.killswitch.set()
        end_critical_section(self.channel, msg="drop lock and join line thread")
        self.join()
        begin_critical_section(self.channel, msg="line thread dead so get lock")


class _Line:
    def __init__(self, channel):
        self.channel        = channel
        self.line           = _State.chip.get_line(channel)
        self.mode           = _line_mode_none
        self.lock           = Lock()
        self.thread         = None
        self.thread_type    = _line_thread_none
        self.callbacks      = []
        self.dutycycle      = -1
        self.frequency      = -1
        self.timestamp      = None

    def thread_start(self, thread_type, args):
        Dprint("ARGS TYPE:", args, type(args))
        self.thread = _LineThread(self.channel, thread_type, args)
        if self.thread:
            DCprint(self.channel, "start thread type {} ".format(thread_type))
            self.thread.start()
            self.thread_type = thread_type
        else:
            DCprint(self.channel, "FAILED to start thread on channel {}".format(self.channel))

        return self.thread is not None

    def thread_stop(self):
        self.thread.kill()
        self.thread = None
        self.thread_type = _line_thread_none

    def cleanup(self):
        if line_is_poll(self.channel):
            line_kill_poll(self.channel)

        if self.line.is_requested():
            self.line.release()
        # We don't want to affect bouncetime handling if channel is used again
        self.dutycycle = -1
        self.frequency = -1
        self.callbacks = []
        self.timestamp = None
        self.mode = _line_mode_none

    def mode_request(self, mode, flags):
        ret = self.line.request(consumer=line_get_unique_name(self.channel), type=mode, flags=flags)
        if ret is None:
            self.mode = mode
        return ret


# Internal library state
class _State:
    mode       = UNKNOWN
    warnings   = True
    debuginfo  = False
    chip       = None
    event_ls   = []
    lines      = []


# === Internal Routines ===

def begin_critical_section(channel, msg="<no msg>"):
    DCprint(channel, "attempt to acquire lock:", msg)
    _State.lines[channel].lock.acquire()
    DCprint(channel, "begin critical section:", msg)


def end_critical_section(channel, msg="<no msg>"):
    DCprint(channel, "end critical section:", msg)
    _State.lines[channel].lock.release()


def Dprint(*msgargs):
    """ Print debug information for development purposes"""
    if _State.debuginfo:
        print("[DEBUG]", *msgargs)


def DCprint(channel, *msgargs):
    Dprint("[{}]".format(channel), *msgargs)


# Reset internal state to default
def Reset():
    Dprint("Reset begins")

    # 1. Kill all running threads
    # 2. Close chip object fd and release any held lines
    #       Note: Bigg critical section (gets all locks)
    cleanup()

    # Reset _State to default values
    _State.mode       = UNKNOWN         # TODO default mode ?
    _State.warnings   = True
    _State.debuginfo  = False
    _State.event_ls   = []

    chip_init_if_needed()
    _State.lines      = [_Line(channel) for channel in range(chip_get_num_lines())]

    Dprint("Reset commplete")


def State_Access():
    # The purpose of this funtion is to allow the user to mess with the
    # internal state of the library for development or recreational purposes
    return _State


def is_all_bools_or_directions(data):
    if not is_iterable(data):
        data = [data]
    if len(data) < 1:
        return False
    return all([(isinstance(elem, bool) or elem in [HIGH, LOW]) for elem in data]) \
        if not (isinstance(data, bool) or data in [HIGH, LOW])\
        else True


def is_all_ints(data):
    if not is_iterable(data):
        data = [data]
    if len(data) < 1:
        return False
    return all([isinstance(elem, int) for elem in data]) \
        if not isinstance(data, int)\
        else True


def is_iterable(data):
    try:
        iter(data)
    except TypeError:
        return False
    else:
        return True


def setdebuginfo(value):
    """Enable or disable debug messages"""
    if not value:
        Dprint("debuginfo output set to", _State.debuginfo)
    _State.debuginfo = bool(value)
    if value:
        Dprint("debuginfo output set to", _State.debuginfo)


def wait_for_edge_validation(edge, bouncetime, timeout):
    if edge not in [RISING, FALLING, BOTH]:
        raise ValueError("The edge must be set to RISING, FALLING or BOTH")

    if bouncetime is not None and bouncetime <= 0:
        raise ValueError("Bouncetime must be greater than 0")

    if timeout and timeout < 0:
        # error semantics differ from RPi.GPIO
        raise ValueError("Timeout must be greater than or equal to 0")


def channel_fix_and_validate_bcm(channel):
    if channel < 0 or channel > chip_get_num_lines() - 1:
        raise ValueError("The channel sent is invalid on a Raspberry Pi")
    else:
        return channel


def channel_fix_and_validate_board(channel):
    if channel < 1 or channel > len(pin_to_gpio_rev3) - 1:
        raise ValueError("The channel sent is invalid on a Raspberry Pi")

    # Use lookup table from RPi.GPIO
    channel = pin_to_gpio_rev3[channel]
    if channel == -1:
        raise ValueError("The channel sent is invalid on a Raspberry Pi")
    else:
        return channel


def channel_fix_and_validate(channel_raw):
    chip_init_if_needed()

    # This function is only defined over three mode settings
    # It should be invariant that mode will contain one of these three values
    # Other values of mode are undefined

    if not isinstance(channel_raw, int):
        raise ValueError("The channel sent is invalid on a Raspberry Pi")

    if _State.mode == UNKNOWN:
        raise RuntimeError("Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)")
    elif _State.mode == BCM:
        return channel_fix_and_validate_bcm(channel_raw)
    elif _State.mode == BOARD:
        return channel_fix_and_validate_board(channel_raw)


def validate_gpio_dev_exists():
    # This function only ever needs to be run once
    if validate_gpio_dev_exists.found:
        return

    gpiochips = []
    for root, dirs, files in os.walk('/dev/'):
        for filename in files:
            if filename.find('gpio') > -1:
                gpiochips.append(filename)
                validate_gpio_dev_exists.found = 1
    if not gpiochips:
        raise ValueError("No compatible chips found")


# Static field
validate_gpio_dev_exists.found = 0


def chip_init():
    # Validate the existence of a gpio character device
    validate_gpio_dev_exists()

    # This is hardcoded for now but that may change soon (or not)
    try:
        _State.chip = gpiod.Chip("gpiochip0")
    except PermissionError:
        print("Unable to access /dev/gpiochip0. Are you sure you have permission?")
        sys.exit()
    Dprint("state chip has value:", _State.chip)


def chip_close():
    _State.chip.close()
    _State.chip = None


def chip_is_open():
    return _State.chip is not None


def chip_init_if_needed():
    if _State.chip is None:
        chip_init()
        Dprint("Chip object init() called")
    else:
        Dprint("NO-OP call to Chip object init()")


def chip_close_if_open():
    if _State.chip is not None:
        Dprint("Chip object close() called")
        chip_close()
    else:
        Dprint("NO-OP call to Chip object close()")


def chip_get_num_lines():
    chip_init_if_needed()
    return _State.chip.num_lines()


def chip_destroy():
    for line in _State.lines:
        begin_critical_section(line.channel, msg="chip destroy begin")
    chip_close_if_open()
    for line in _State.lines:
        end_critical_section(line.channel, msg="chip destory end")


def line_get_unique_name(channel):
    chip_init_if_needed()
    return str(_State.chip.name()) + "-" + str(channel)


def line_set_mode(channel, mode, flags=0):
    DCprint(channel, "attempt", mode, "set_mode (current value {})".format(line_get_mode(channel)))
    if mode == line_get_mode(channel):
        DCprint(channel, " ==> NOOP set_mode")
        return

    begin_critical_section(channel, msg="set line_mode")
    if line_get_mode(channel) != _line_mode_none or mode == _line_mode_none:
        DCprint
        _State.lines[channel].cleanup()

    if mode != _line_mode_none:
        ret = _State.lines[channel].mode_request(mode, flags)
        DCprint(channel, "ioctl/request({}, {}) rv:".format(mode, flags), ret)

    end_critical_section(channel, msg="set line_mode")
    DCprint(channel, "line mode set to", mode)


def line_get_mode(channel):
    return _State.lines[channel].mode


def line_is_active(channel):
    return line_get_mode(channel) != _line_mode_none


def line_get_active_state(channel):
    return _State.lines[channel].line.active_state()


def line_get_direction(channel):
    return _LINE_MODE_TO_DIR_CONST[line_get_mode(channel)]


def line_get_bias(channel):
    return _State.lines[channel].line.bias()


# Since libgpiod does not expose a get_flags option, we roll our own here
# by bitwise OR'ing all the flag getters that we use
_LIBGPIOD_FLAG_GETTERS = {
    line_get_bias: bias_flag,
    line_get_active_state: active_flag,
}


def line_get_flags(channel):
    flags = 0
    for getter, to_flag in _LIBGPIOD_FLAG_GETTERS.items():
        flags |= to_flag(getter(channel))
    return flags


def line_set_flags(channel, flags):
    begin_critical_section(channel, msg="set flags")
    DCprint(channel, "set flags:", flags)
    _State.lines[channel].line.set_flags(flags)
    end_critical_section(channel, msg="set flags")


def line_poll_start(channel, edge, callback, bouncetime):

    begin_critical_section(channel, msg="start poll")

    if callback:
        _State.lines[channel].callbacks.append(callback)
    # Start a thread that polls for events on the pin and create a list of event callbacks
    # OLD way
    #_State.lines[channel].thread = _LineThread(channel, _line_thread_poll, args=(channel, edge, callback, bouncetime))
    _State.lines[channel].thread_start(_line_thread_poll, args=(channel, edge, callback, bouncetime))

    # Start the edge detection thread FIXME already started
    #_State.lines[channel].thread_start()

    end_critical_section(channel, msg="start poll")


def line_pwm_start(channel, dutycycle):
    # The user would first call init to set
    # Line.frequency to a non-negative (valid) value
    # and so we validate that we are in a state
    # where the user has called PWM.__init__()
    # but there is not yet a thread running
    if not line_is_pwm(channel) and \
            line_pwm_get_frequency(channel) != -1:
        begin_critical_section(channel, msg="pwm start")

        # If you forgot to setup this channel as an output, we've got you
        line_set_mode(channel, _line_mode_out)

        line_pwm_set_dutycycle(channel, dutycycle)
        _State.lines[channel].thread_start(_line_thread_pwm, args=(channel,))

        end_critical_section(channel, msg="pwm start")
        return line_is_pwm(channel)
    else:
        warn("invalid call to pwm_start(). Did you call PWM.__init__() on this channel?")
        return False

    # If the line is already running a PwM thread
    # return True, but if there is no thread running
    # and the user tried to call PWM.start() before
    # calling PWM.__init__() somewhow, then
    # return False and tell them to call init.


def line_pwm_stop(channel):
    if line_is_pwm(channel):
        begin_critical_section(channel, msg="pwm stop")
        _State.lines[channel].thread_stop()
        end_critical_section(channel, msg="pwm stop")


def line_pwm_set_dutycycle(channel, dutycycle):
    _State.lines[channel].dutycycle = dutycycle


def line_pwm_set_dutycycle_lock(channel, dutycycle):
    begin_critical_section(channel, msg="set dutycycle")
    line_pwm_set_dutycycle(channel, dutycycle)
    end_critical_section(channel, msg="set dutycycle")


def line_pwm_get_dutycycle(channel):
    return _State.lines[channel].dutycycle


def line_pwm_set_frequency(channel, frequency):
    begin_critical_section(channel, msg="set frequency")
    _State.lines[channel].frequency = frequency
    end_critical_section(channel, msg="set frequency")


def line_pwm_get_frequency(channel):
    return _State.lines[channel].frequency


def line_is_pwm(channel):
    DCprint(channel, "checking if channel is pwm:", _State.lines[channel].thread_type == _line_thread_pwm)
    return _State.lines[channel].thread_type == _line_thread_pwm


def line_is_poll(channel):
    DCprint(channel, "checking if channel is poll:", _State.lines[channel].thread_type == _line_thread_poll)
    return _State.lines[channel].thread_type == _line_thread_poll


# Requires lock
def line_kill_poll(channel):
    _State.lines[channel].thread_stop()


def line_kill_poll_lock(channel):
    begin_critical_section(channel, msg="kill poll lock")
    line_kill_poll(channel)
    end_critical_section(channel, msg="kill poll lock")


def line_set_value(channel, value):
    DCprint(channel, "Set value to", value)
    _State.lines[channel].line.set_value(value)


def line_get_value(channel):
    return _State.lines[channel].line.get_value()


def line_event_wait_lock(channel, bouncetime, timeout):
    begin_critical_section(channel, msg="event wait")
    ret = line_event_wait(channel, bouncetime, timeout)
    end_critical_section(channel, msg="event wait")
    return ret


# requires lock
def line_event_wait(channel, bouncetime, timeout):
    # Split up timeout into appropriate parts
    timeout_sec     = int(int(timeout) / 1000)
    timeout_nsec    = (int(timeout) % 1000) * 1000

    ret = None

    # We only care about bouncetime if it is explicitly speficied in the call to this function or if
    # this is not the first call to wait_for_edge on the specified pin
    if bouncetime and _State.lines[channel].timestamp and \
            time.time() - _State.lines[channel].timestamp < bouncetime:
        pass
    elif _State.lines[channel].line.event_wait(sec=timeout_sec, nsec=timeout_nsec):
        _State.lines[channel].timestamp = time.time()
        if channel not in _State.event_ls:
            # Ensure no double appends. FIXME: should this be done outside of a poll thread?
            _State.event_ls.append(channel)
        event = _State.lines[channel].line.event_read()

        # A hack to clear the event buffer by reading a bunch of bytes
        # from the underlying file representing the GPIO line
        eventfd = _State.lines[channel].line.event_get_fd()
        os.read(eventfd, 10000)
        if event:
            ret = channel

    return ret


def line_add_callback(channel, callback):
    begin_critical_section(channel, "add callback")
    _State.lines[channel].callbacks.append(callback)
    end_critical_section(channel, "add callback")


def line_thread_should_die(channel):
    return _State.lines[channel].thread.killswitch.is_set()


TEN_MILLISECONDS_IN_SECONDS = 0.0010


def line_do_poll(channel, bouncetime, timeout):

    while True:
        begin_critical_section(channel, msg="do poll")
        if line_thread_should_die(channel):
            end_critical_section(channel, msg="do poll exit")
            break
        if line_event_wait(channel, bouncetime, timeout):
            callbacks = _State.lines[channel].callbacks
            for fn in callbacks():
                fn()
        end_critical_section(channel, msg="do poll")
        time.sleep(TEN_MILLISECONDS_IN_SECONDS)


def poll_thread(channel, edge, callback, bouncetime):

    # FIXME: this is arbitrary
    timeout = 10  # milliseconds
    wait_for_edge_validation(edge, bouncetime, timeout)

    DCprint(channel, "launch poll thread")
    line_do_poll(channel, bouncetime, timeout)
    DCprint(channel, "terminate poll thread")


# NOTE: RPi.GPIO specifies:
# Default to 1 kHz frequency 0.0% dutycycle
# but interface functions require explicit arguments
def pwm_thread(channel):
    DCprint(channel, "begin PwM thread with dutycycle {}% and frequency {} Hz".format(_State.lines[channel].dutycycle,
                                                                                      _State.lines[channel].frequency))

    # We wrap the loop with a try except so we can drop the lock and exit if
    # access to the channel is suddenly revoked by the main thread
    try:
        while True:
            begin_critical_section(channel, msg="do pwm")
            if line_thread_should_die(channel):
                end_critical_section(channel, msg="do pwm exit")
                break
            if _State.lines[channel].dutycycle > 0:
                line_set_value(channel, True)
                DCprint(channel, "PwM: ON")
                # PwM calculation for high voltage part of period:
                time.sleep(1 / _State.lines[channel].frequency * (_State.lines[channel].dutycycle / 100.0))
            if _State.lines[channel].dutycycle < 100:
                line_set_value(channel, False)
                DCprint(channel, "PwM: OFF")
                # PwM calculation for low voltage part of period:
                time.sleep(1 / _State.lines[channel].frequency * (1.0 - _State.lines[channel].dutycycle / 100.0))
            end_critical_section(channel, msg="do pwm")
            time.sleep(TEN_MILLISECONDS_IN_SECONDS)
            # arbitrary time to sleep without lock
            # TODO: may interfere with overall timing of PwM but it's rough anyway
    except (ValueError, PermissionError):
        # If this thread suddenly fails to access a channel, exit gracefully
        end_critical_section(channel, msg="do pwm sudden exit")


# === RPi.GPIO API entry points ===


def add_event_callback(channel, callback):
    """
    Add a callback for an event already defined using add_event_detect()
    channel      - either board pin number or BCM number depending on which mode is set.
    callback     - a callback function"

    {compat} we do not require that the channel be setup as an input
    """

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    if not line_is_poll(channel):
        raise RuntimeError("Add event detection using add_event_detect first before adding a callback")

    if not callable(callback):
        raise TypeError("Parameter must be callable")

    line_add_callback(channel, callback)


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

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    valid_edges = [RISING, FALLING, BOTH]
    if edge not in valid_edges:
        raise ValueError("The edge must be set to RISING, FALLING or BOTH")

    if callback and not callable(callback):
        raise TypeError("Parameter must be callable")

    if bouncetime and bouncetime <= 0:
        raise ValueError("Bouncetime must be greater than 0")

    line_set_mode(channel, edge)
    line_poll_start(channel, edge, callback, bouncetime)


def channel_valid_or_die(channel):
    """
    Validate a channel/pin number
    Returns the pin number on success otherwise throws a ValueError

        channel        - an integer to be validated as a channel
    """
    channel_fix_and_validate(channel)


def cleanup(channels=None):
    """
    Clean up by resetting all GPIO channels that have been used by this program to INPUT with no pullup/pulldown and no event detection
    [channel] - individual channel or list/tuple of channels to clean up.
    Default - clean every channel that has been used.

    {compat} Cleanup is mostly handled by libgpiod and the kernel, but we use this opportunity to kill any running callback poll threads
        as well as close any open file descriptors
    """

    if not chip_is_open():
        chip_init_if_needed()
        _State.lines = [_Line(channel) for channel in range(chip_get_num_lines())]

    destroy = False
    if channels is None:
        destroy = True
        channels = [i for i in range(chip_get_num_lines())]

    if not is_all_ints(channels):
        raise ValueError("Channel must be an integer or list/tuple of integers")
    elif isinstance(channels, tuple):
        # Convert tuples to lists to make them writable for normalization of values
        channels = [c for c in channels]

    if not destroy:
        Dprint("NOT DESTROY: iterable=", is_iterable(channels))
        if not is_iterable(channels):
            channels = [channels]
        for i in range(len(channels)):
            # This implements BOARD mode
            channels[i] = channel_fix_and_validate(channels[i])

    Dprint("cleanup {} lines".format(len(channels)))
    if not destroy:
        Dprint("channels:", channels)
    for chan in channels:
        line_set_mode(chan, _line_mode_none)

    if destroy:
        chip_destroy()


def event_detected(channel):
    """
    Returns True if an edge has occurred on a given GPIO.  You need to enable edge detection using add_event_detect() first.
    channel - either board pin number or BCM number depending on which mode is set."
    """

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    if channel in _State.event_ls:
        _State.event_ls.remove(channel)
        return True
    else:
        return False


def getactive_state(channel):
    """
    Get the active_state of an active channel
    Returns HIGH or LOW if the channel is active and -1 otherwise
    """

    channel = channel_fix_and_validate(channel)

    if line_is_active(channel):
        return line_get_active_state(channel)
    else:
        return -1


def getbias(channel):
    """
    Get bias mode of an active channel
    Returns PUD_OFF, PUD_DOWN, PUD_UP, or PUD disabled if the channel is
        active or just PUD_OFF if the channel is not active.
    """

    channel = channel_fix_and_validate(channel)

    if line_is_active(channel):
        return line_get_bias(channel)
    else:
        return PUD_OFF


def getdirection(channel):
    """
    Get direction of an active channel
    Returns OUT if the channel is in an output mode, IN if the channel is in an input mode,
    and -1 otherwise
    """

    channel = channel_fix_and_validate(channel)
    return line_get_direction(channel)


def getmode():
    """
    Get numbering mode used for channel numbers.
    Returns BOARD, BCM or None
    """

    return _State.mode if _State.mode else None


def gpio_function(channel):
    """
    Return the current GPIO function (IN, OUT, PWM, SERIAL, I2C, SPI)
    channel - either board pin number or BCM number depending on which mode is set.

    {compat} This is a stateless function that will return a constant value for every pin
    """

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    mode = line_get_mode(channel)

    if mode == _line_mode_out:
        return OUT
    elif mode == _line_mode_in:
        return IN
    else:
        return UNKNOWN

    # We will provide support for other potential values of gpio_function
    # when the underlying functions (SPI, SERIAL, I2C, HARD_PWM) are implemented.


def input(channel):
    """
    Input from a GPIO channel.  Returns HIGH=1=True or LOW=0=False
    # channel - either board pin number or BCM number depending on which mode is set.
    """

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    # this does't really make sense but it matches rpi gpio source code logic
    if getdirection(channel) not in [IN, OUT]:
        raise RuntimeError("You must setup() the GPIO channel first")

    # TODO I feel like we should do more validation

    return line_get_value(channel)


def output(channel, value):
    """
    Output to a GPIO channel or list of channel
    channel - either board pin number or BCM number depending on which mode is set.
    value   - 0/1 or False/True or LOW/HIGH

    {compat} channel and value parameters may be lists or tuples of equal length
    """
    if not is_all_ints(channel):
        raise ValueError("Channel must be an integer or list/tuple of integers")

    if not is_iterable(channel):
        channel = [channel]

    if (not is_all_ints(value)) and (not is_all_bools_or_directions(value)):
        raise ValueError("Value must be an integer/boolean or a list/tuple of integers/booleans")

    # Convert tuples to lists to make them writable for normalization of values
    if isinstance(value, tuple):
        value = [v for v in value]

    # If there is a single value provided, we set each channel to that value
    if not is_iterable(value):
        value = [value for i in range(len(channel))]

    # This implements BOARD mode for all input cases
    for i in range(len(channel)):
        channel[i] = channel_fix_and_validate(channel[i])

    # Normalize the value argument
    for i in range(len(value)):
        if value[i] == HIGH:
            value[i] = True
        if value[i] == LOW:
            value[i] = False

    Dprint("channel", channel, "value", value)
    if len(channel) != len(value):
        raise RuntimeError("Number of channel != number of value")

    for chan, val in zip(channel, value):
        if line_get_mode(chan) != _line_mode_out:
            warn("The GPIO channel has not been set up as an OUTPUT\n\tSkipping channel {}".format(chan))
        else:
            try:
                line_set_value(chan, bool(val))
            except PermissionError:
                warn("Unable to set value of channel {}, did you forget to run setup()? Or did setup() fail?".format(chan))


def remove_event_detect(channel):
    """
    Remove edge detection for a particular GPIO channel
    channel - either board pin number or BCM number depending on which mode is set.
    """

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    if line_is_poll(channel):
        line_kill_poll_lock(channel)
    else:
        raise ValueError("event detection not setup on channel {}".format(channel))


def setactive_state(channel, active_state):
    """
    Set the active_state of an active channel
    """

    channel = channel_fix_and_validate(channel)

    if active_state not in [HIGH, LOW]:
        raise ValueError("An active state was passed to setactive_state()")

    current = getactive_state(channel)
    if active_state != current:
        flags = line_get_flags(channel)
        flags &= ~active_flag(getactive_state(channel))
        flags |= active_flag(active_state)
        line_set_flags(channel, flags)


def setbias(channel, bias):
    """
    Set bias of an active channel
    """

    channel = channel_fix_and_validate(channel)

    if bias not in [PUD_OFF, PUD_UP, PUD_DOWN, PUD_DISABLE]:
        raise ValueError("An invalid bias was passed to setbias()")

    current = getbias(channel)
    if bias != current:
        flags = line_get_flags(channel)
        flags &= ~bias_flag(getbias(channel))
        flags |= bias_flag(bias)
        line_set_flags(channel, flags)


def setdirection(channel, direction):
    """
    Set direction of an active channel
    """

    channel = channel_fix_and_validate(channel)

    if direction != IN and direction != OUT:
        raise ValueError("An invalid direction was passed to setdirection()")

    current = line_get_direction(channel)
    if current != -1:
        if current == IN and direction == OUT:
            line_set_mode(channel, _line_mode_out)
        elif current == OUT and direction == IN:
            line_set_mode(channel, _line_mode_in)


def setmode(mode):
    """
    Set up numbering mode to use for channels.
        BOARD - Use Raspberry Pi board numbers
        BCM   - Use Broadcom GPIO 00..nn numbers
    """
    if _State.mode != UNKNOWN:
        raise ValueError("A different mode has already been set!")

    if mode != BCM and mode != BOARD:
        raise ValueError("An invalid mode was passed to setmode()")

    _State.mode = mode

    chip_init_if_needed()

    Dprint("mode set to", _State.mode)


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

    if pull_up_down not in [PUD_OFF, PUD_UP, PUD_DOWN, PUD_DISABLE]:
        raise ValueError("Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP, PUD_DOWN, or PUD_DISABLE")

    # Convert tuples to lists to make them writable for validations of channels
    if isinstance(channel, tuple):
        channel = [c for c in channel]

    # Make the channel data iterable by force
    if not is_iterable(channel):
        channel = [channel]

    # This implements BOARD mode
    for i in range(len(channel)):
        channel[i] = channel_fix_and_validate(channel[i])

    request_flags = 0
    request_flags |= bias_flag(pull_up_down)

    for pin in channel:
        try:
            line_set_mode(pin, direction, request_flags)
            if initial is not None:
                line_set_value(pin, initial)
        except OSError:
            warn("This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.\n \
                    Further attemps to use channel {} will fail unless setup() is run again sucessfully".format(pin))


def setwarnings(value):
    """Enable or disable warning messages"""
    _State.warnings = bool(value)
    Dprint("warning output set to", _State.warnings)


def wait_for_edge(channel, edge, bouncetime=None, timeout=0):
    """
    Wait for an edge.  Returns the channel number or None on timeout.
    channel      - either board pin number or BCM number depending on which mode is set.
    edge         - RISING, FALLING or BOTH
    [bouncetime] - time allowed between calls to allow for switchbounce
    [timeout]    - timeout in ms

    {compat} bouncetime units are in seconds. this is subject to change
    """

    # Running this function before setup is allowed but the initial pin value is undefined
    # RPi.GPIO requires one to setup a pin as input before using it for event detection,
    # while libgpiod provides an interface that keeps the two mutually exclusive. We get around
    # this by not requiring it, though to maintain the same semantics as RPi.GPIO, we attempt
    # to release the channel's handle as a an input value, and acquire a new handle for an
    # event value.

    # This implements BOARD mode
    channel = channel_fix_and_validate(channel)

    wait_for_edge_validation(edge, bouncetime, timeout)

    # ensure the line is in the right mode
    # FIXME does this break input mode?
    try:
        line_set_mode(channel, edge)
    except OSError:
        raise RuntimeError("Channel is currently in use (Device or Resource Busy)")

    return line_event_wait_lock(channel, bouncetime, timeout)


# === RPi.GPIO Pulse-width Modulation (PwM) class ===


class PWM:
    def __init__(self, channel, frequency):
        channel = channel_fix_and_validate(channel)

        if line_get_mode(channel) != _line_mode_out:
            raise RuntimeError("You must setup() the GPIO channel as an output first")

        # If frequency is not -1 then we have called init() but not yet called start() so raise exception
        if line_is_pwm(channel) or line_pwm_get_frequency(channel) != -1:
            raise RuntimeError("A PWM object already exists for this GPIO channel")

        if frequency <= 0.0:
            raise ValueError("frequency must be greater than 0.0")
        self.channel = channel
        line_pwm_set_frequency(channel, frequency)

    def start(self, dutycycle):
        """
        Start software PWM
        dutycycle - the duty cycle (0.0 to 100.0)
        """
        if dutycycle < 0.0 or dutycycle > 100.0:
            raise ValueError("dutycycle must have a value from 0.0 to 100.0")

        return line_pwm_start(self.channel, dutycycle)

    def stop(self):
        """
        Stop software PWM
        """
        line_pwm_stop(self.channel)

    def ChangeDutyCycle(self, dutycycle):
        """
        Change the duty cycle
        dutycycle - between 0.0 and 100.0
        """
        if dutycycle < 0.0 or dutycycle > 100.0:
            raise ValueError("dutycycle must have a value from 0.0 to 100.0")

        line_pwm_set_dutycycle_lock(self.channel, dutycycle)

    def ChangeFrequency(self, frequency):
        """
        Change the frequency
        frequency - frequency in Hz (freq > 1.0)
        """

        if frequency <= 0.0:
            raise ValueError("frequency must be greater than 0.0")

        line_pwm_set_frequency(self.channel, frequency)


# === Library initialization ===


# Initialize the library with a reset
Reset()


# line thead type to callable entry point mapping
_LINE_THREAD_TYPE_TO_TARGET = {
    _line_thread_poll:  poll_thread,
    _line_thread_pwm:   pwm_thread,
}

# Run cleanup() when an interpreter using this module terminates
atexit.register(cleanup)
