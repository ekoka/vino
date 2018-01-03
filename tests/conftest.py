import pytest
import logging

@pytest.fixture('session')
def logger():
    logger = logging.getLogger('vino')
    logger.addHandler(logging.FileHandler('logs/codin.log'))
    return logger

