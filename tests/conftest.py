import pytest
import logging
import random
from string import ascii_letters, digits

@pytest.fixture('session')
def logger():
    logger = logging.getLogger('vino')
    logger.addHandler(logging.FileHandler('logs/codin.log'))
    return logger

@pytest.fixture
def processors():
    length = 5
    def create_fnc(i):
        return lambda: i
    processors = [create_fnc(i) for i in range(length)]
    return processors

@pytest.fixture
def randstr():
    s = ascii_letters+digits
    return ''.join([s[random.randint(0,25)] for i in range(15)])


