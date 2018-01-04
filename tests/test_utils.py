import pytest
from vino import utils

def test_is_numberlike_int():
    assert utils.is_numberlike(2)
def test_is_numberlike_float():
    assert utils.is_numberlike(2.2)
def test_is_numberlike_neg_int():
    assert utils.is_numberlike(-2)
def test_is_numberlike_neg_float():
    assert utils.is_numberlike(-2.3)
def test_is_not_numberlike_str():
    assert not utils.is_numberlike('2')

def test_is_str():
    assert utils.is_str('some string')
def test_is_str_empty():
    assert utils.is_str('')
def test_is_not_str_tuple():
    assert not utils.is_str(tuple('abc'))

def test_is_boolean_false(): 
    assert utils.is_boolean(False)
def test_is_boolean_true(): 
    assert utils.is_boolean(True)
def test_is_not_boolean_empty_str(): 
    assert not utils.is_boolean('')
def test_is_not_boolean_None(): 
    assert not utils.is_boolean(None)
