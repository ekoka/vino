import pytest
from vino.errors import VinoError, ValidationError, ValidationErrorStack

@pytest.fixture
def e_stack(): 
    rv = ValidationErrorStack('Stack of errors')
    for i in range(5):
        try:
            raise ValidationError('error '+str(i))
        except ValidationError as e:
            rv.append(e)
    return rv

def test_ValidationError_has_interrupt_validation_attribute():
    try:
        raise ValidationError('test')
    except ValidationError as e:
        assert hasattr(e,'interrupt_validation')

def test_ValidationErrorStack_acts_like_list_on_append(e_stack):
    assert len(e_stack.errors)==5

def test_ValidationErrorStack_acts_like_list_on_len(e_stack):
    assert len(e_stack)==5

def test_ValidationErrorStack_acts_is_indexable(e_stack):
    e = e_stack[0]
    assert isinstance(e, ValidationError)
    with pytest.raises(IndexError) as e:
        e = e_stack[5]

def test_VEStack_empty_flag_true_if_has_errors():
    stack = ValidationErrorStack('stack')
    assert stack.empty
    stack.append(ValidationError('new error'))
    assert not stack.empty
    e = stack.pop()
    assert stack.empty

def test_VEStack_can_be_cleared():
    stack = ValidationErrorStack('stack')
    stack.append(ValidationError('new error'))
    assert not stack.empty
    stack.clear()
    assert stack.empty
