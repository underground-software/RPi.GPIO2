import gpiod
import pytest
import re

def foo():
    pass

def test_is_all_ints():
    invalid_data = ['a', {'a':5}, foo]
    valid_data = [1, [1,2,3,4], 10000]
    for i in invalid_data:
        assert gpiod.is_all_ints(i) == False
    for i in valid_data:
        assert gpiod.is_all_ints(i) == True

def test_is_all_bools():
    invalid_data = [foo, None, 5]
    valid_data = [True, False]
    for i in invalid_data:
        assert gpiod.is_all_bools(i) == False
    for i in valid_data:
        assert gpiod.is_all_bools(i) == True

def test_is_iterable():
    a = re.compile('[\d]+')
    invalid_data = [None, 1, foo, a]
    valid_data = ["a", "iter", [], [1,2,3]]
    for i in invalid_data:
        assert gpiod.is_all_bools(i) == False
    for i in valid_data:
        assert gpiod.is_all_bools(i) == True

def test_setmode_raise_double_setup_exception():
    with pytest.raises(Exception):
        gpiod.setmode(gpiod.BCM)
        gpiod.setmode(gpiod.BOARD)

def test_setmode_raise_invalid_mode_exception():
    with pytest.raises(Exception):
        gpiod.setmode(5)
    with pytest.raises(Exception):
        gpiod.setmode('a')
    with pytest.raises(Exception):
        gpiod.setmode([])

def test_output_raise_value_errors():
    with pytest.raises(Exception):
        gpiod.output([1,2,3],[1,2,3,4])
    with pytest.raises(Exception):
        gpiod.output([],[])

def test_getmode():
    gpiod._State.mode = gpiod.BOARD
    assert gpiod.test_getmode == gpiod.BOARD

    gpiod._State.mode = gpiod.BCM
    assert gpiod.test_getmode == gpiod.BCM

    gpiod._State.mode = None
    assert gpiod.test_getmode == None

def test_validate_pin_or_die():
    

