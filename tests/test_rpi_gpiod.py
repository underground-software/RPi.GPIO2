import RPi.GPIO as GPIO
import pytest
import re
import os

def foo():
    pass

def test_is_all_ints():
    GPIO.Reset()
    invalid_data = ['a', {'a':5}, foo]
    valid_data = [1, [1,2,3,4], 10000]
    for i in invalid_data:
        assert GPIO.is_all_ints(i) == False
    for i in valid_data:
        assert GPIO.is_all_ints(i) == True

def test_is_all_bools():
    GPIO.Reset()
    invalid_data = [foo, None, 5]
    valid_data = [True, False]
    for i in invalid_data:
        assert GPIO.is_all_bools(i) == False
    for i in valid_data:
        assert GPIO.is_all_bools(i) == True

def test_is_iterable():
    GPIO.Reset()
    a = re.compile(r'[\d]+')
    invalid_data = [None, 1, foo, a]
    valid_data = ["a", "iter", [], [1,2,3]]
    for i in invalid_data:
        assert GPIO.is_iterable(i) == False
    for i in valid_data:
        assert GPIO.is_iterable(i) == True

def test_setmode_raise_double_setup_exception():
    GPIO.Reset()
    with pytest.raises(Exception):
        GPIO.setmode(GPIO.BCM)
        GPIO.setmode(GPIO.BOARD)

def test_setmode_raise_invalid_mode_exception():
    GPIO.Reset()
    with pytest.raises(Exception):
        GPIO.setmode(5)
    with pytest.raises(Exception):
        GPIO.setmode('a')
    with pytest.raises(Exception):
        GPIO.setmode([])

def test_output_raise_value_errors():
    GPIO.Reset()
    with pytest.raises(Exception):
        GPIO.output([1,2,3],[1,2,3,4])
    with pytest.raises(Exception):
        GPIO.output([],[])

def test_getmode():
    GPIO.Reset()
    GPIO.State_Access().mode = GPIO.BOARD
    assert GPIO.getmode() == GPIO.BOARD

    GPIO.State_Access().mode = GPIO.BCM
    assert GPIO.getmode() == GPIO.BCM

    GPIO.State_Access().mode = None
    assert GPIO.getmode() == None

    GPIO.Reset()

def test_validate_pin_or_die():
    GPIO.Reset()
    pass    


def test_set_mode():
    GPIO.Reset()

    with pytest.raises(ValueError):
        GPIO.setmode(23)

    GPIO.setmode(GPIO.BCM)

    with pytest.raises(ValueError):
        GPIO.setmode(GPIO.BOARD)

    with pytest.raises(ValueError):
        GPIO.setmode(GPIO.UNKNOWN)

    GPIO.Reset()
    # Cannot use this yet
    # with os.setuid(1):
    #     GPIO.setmode(GPIO.BCM)

    # Board mode is not currently supported (TODO)
    with pytest.raises(ValueError):
        GPIO.setmode(GPIO.BOARD)
