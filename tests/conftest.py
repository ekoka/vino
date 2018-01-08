import pytest
import logging
import random
from string import ascii_letters, digits
from vino.errors import ValidationError

@pytest.fixture('session')
def logger():
    rv = logging.getLogger('vino')
    rv.addHandler(logging.FileHandler('logs/codin.log'))
    return rv

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

@pytest.fixture
def tags():
    def bold(value, context):
        return '<b>'+value+'</b>'
    def italic(value, context):
        return '<i>'+value+'</i>'
    def underline(value, context):
        return '<u>'+value+'</u>'
    return bold, italic, underline 

@pytest.fixture
def fails_continue():
    def fail1(value, context):
        raise ValidationError('first failure', False)
    def fail2(value, context):
        raise ValidationError('second failure', False)
    def fail3(value, context):
        raise ValidationError('third failure', False)
    return fail1, fail2, fail3
