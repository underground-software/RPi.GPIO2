from .. import GPIO
import pytest
import re

def foo():
    pass

def test_is_all_ints():
    invalid_data = ['a', {'a':5}, foo]
    valid_data = [1, [1,2,3,4], 10000]
    for i in invalid_data:
        assert GPIO.is_all_ints(i) == False
    for i in valid_data:
        assert GPIO.is_all_ints(i) == True

def test_is_all_bools():
    invalid_data = [foo, None, 5]
    valid_data = [True, False]
    for i in invalid_data:
        assert GPIO.is_all_bools(i) == False
    for i in valid_data:
        assert GPIO.is_all_bools(i) == True

def test_is_iterable():
    a = re.compile(r'[\d]+')
    invalid_data = [None, 1, foo, a]
    valid_data = ["a", "iter", [], [1,2,3]]
    for i in invalid_data:
        assert GPIO.is_iterable(i) == False
    for i in valid_data:
        assert GPIO.is_iterable(i) == True

def test_setmode_raise_double_setup_exception():
    with pytest.raises(Exception):
        GPIO.setmode(GPIO.BCM)
        GPIO.setmode(GPIO.BOARD)

def test_setmode_raise_invalid_mode_exception():
    with pytest.raises(Exception):
        GPIO.setmode(5)
    with pytest.raises(Exception):
        GPIO.setmode('a')
    with pytest.raises(Exception):
        GPIO.setmode([])

def test_output_raise_value_errors():
    with pytest.raises(Exception):
        GPIO.output([1,2,3],[1,2,3,4])
    with pytest.raises(Exception):
        GPIO.output([],[])

def test_getmode():
    GPIO._State.mode = GPIO.BOARD
    assert GPIO.getmode() == GPIO.BOARD

    GPIO._State.mode = GPIO.BCM
    assert GPIO.getmode() == GPIO.BCM

    GPIO._State.mode = None
    assert GPIO.getmode() == None

def test_validate_pin_or_die():
    pass    

