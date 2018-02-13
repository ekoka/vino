import pytest
import logging
import random
from string import ascii_letters, digits
from vino import errors as err
from vino import contexts as ctx

def pytest_itemcollected(item):
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))

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
    def bold(value, state):
        return '<b>'+value+'</b>'
    def italic(value, state):
        return '<i>'+value+'</i>'
    def underline(value, state):
        return '<u>'+value+'</u>'
    return bold, italic, underline 

@pytest.fixture
def fails_continue():
    def fail1(value, state):
        raise err.ValidationError('first failure', False)
    def fail2(value, state):
        raise err.ValidationError('second failure', False)
    def fail3(value, state):
        raise err.ValidationError('third failure', False)
    return fail1, fail2, fail3
