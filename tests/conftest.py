import pytest
import logging
import random
from string import ascii_letters, digits
from vino import errors as err
from vino import contexts as ctx

@pytest.fixture('session')
def logger():
    rv = logging.getLogger('vino')
    rv.addHandler(logging.FileHandler('logs/codin.log'))
    return rv

@pytest.fixture
def context():
    class TestContext(ctx.Context): pass
    return TestContext

@pytest.fixture
def processors():
    length = 5
    def create_fnc(i):
        return (lambda: i), None
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
        raise err.ValidationError('first failure', False)
    def fail2(value, context):
        raise err.ValidationError('second failure', False)
    def fail3(value, context):
        raise err.ValidationError('third failure', False)
    return fail1, fail2, fail3
