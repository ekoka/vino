import pytest

from vino import contexts
from vino import errors as err
from vino.processors import runners, processors as proc

class TestArrayContext:
    def test_can_validate_listlike_data(self):
        # here we're just happy that it doesn't raise any errors
        c = contexts.ArrayContext()
        c.validate(list('abcd'))
        c.validate(tuple('abcd'))

    def test_converts_array_and_tuple_data_to_list(self):
        c = contexts.ArrayContext()
        s = 'abcd'
        for f in [list, tuple]:
            rv = c.validate(f(s))
            assert rv==list(s)

    def test_accepts_empty_list(self):
        c = contexts.ArrayContext()
        c.validate([])

    def test_accepts_None(self):
        c = contexts.ArrayContext()
        c.validate(None)

    def test_rejects_sets(self):
        c = contexts.ArrayContext()
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate(set('abcd'))
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is set

    def test_rejects_dict(self):
        c = contexts.ArrayContext()
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate({'a':'a', 'b':'c', 'c':'d'})
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is dict

    def test_rejects_str(self):
        c = contexts.ArrayContext()
        with pytest.raises(err.ValidationErrorStack) as exc_info:
            rv = c.validate('abcd')
        err_stack = exc_info.value
        error = err_stack[0]
        assert 'wrong type' in error.args[0].lower()
        assert error.args[1] is str

    @pytest.mark.skip
    def test_can_have_multiple_array_item_contexts():
        assert False

@pytest.mark.skip
class TestArrayItemContext:

    def test_processes_array_items():
        assert False

    def test_processes_all_items_if_no_qualifier():
        assert False

    def test_processes_only_qualified_items():
        assert False

    def test_can_qualify_a_single_item():
        assert False

    def test_can_have_multiple_qualifiers():
        assert False
