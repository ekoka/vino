from vino.contexts import ObjectContext
from vino import errors as err
import pytest

class TestObjectContext:

    def test_validating_empty_object_returns_empty_obj(self):
        c = ObjectContext()
        rv = c.validate({})
        assert rv=={}

    def test_validating_null_object_returns_null_by_default(self):
        c = ObjectContext()
        rv = c.validate(None)
        assert rv is None

    def test_validation_return_value_has_same_values(self):
        c = ObjectContext()
        value = {'a':23, 'b':12}
        rv = c.validate(value)
        assert rv==value

    def test_validation_return_value_is_not_original_object(self):
        c = ObjectContext()
        value = {'a':23, 'b':12}
        rv = c.validate(value)
        assert rv is not value 

    def test_validation_rejects_list_type(self):
        c = ObjectContext()
        value = ['a',23,'b',12]
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is list

    def test_validation_rejects_tuple_type(self):
        c = ObjectContext()
        value = ('a',23, 'b',12)
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is tuple

    def test_validation_rejects_strings(self):
        c = ObjectContext()
        value = 'abcdelf'
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is str

    def test_validation_rejects_empty_strings(self):
        c = ObjectContext()
        value = ''
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is str

    def test_validation_rejects_empty_list(self):
        c = ObjectContext()
        value = []
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is list

    def test_validation_rejects_empty_tuple(self):
        c = ObjectContext()
        value = ()
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is tuple
        
    def test_validation_rejects_list_of_tuples(self):
        c = ObjectContext()
        value = (('a',23), ('b',12))
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(value)
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is tuple
