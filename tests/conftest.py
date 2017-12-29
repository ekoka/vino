import vino
import pytest
import logging

@pytest.fixture
def filters():
    from vino import filters
    return filters

@pytest.fixture('session')
def logger():
    logger = logging.getLogger('vino')
    logger.addHandler(logging.FileHandler('logs/codin.log'))
    return logger

