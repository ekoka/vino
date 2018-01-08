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

class TestArrayItemContext:

    def test_can_contain_processors(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        assert len(c._runners)==len(tags)

    def test_after_validate_array_has_same_length(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        value = ['a']
        rv = c.validate(value)
        assert len(rv)==len(value)

    def test_validate_first_array_item(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        value = ['a']
        rv = c.validate(value)
        assert rv[0]=='<u><i><b>a</b></i></u>'

    def test_validate_multiple_array_items(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        value = ['a', 'b', 'c']
        rv = c.validate(value)
        assert rv[0]=='<u><i><b>a</b></i></u>'
        assert rv[1]=='<u><i><b>b</b></i></u>'
        assert rv[2]=='<u><i><b>c</b></i></u>'

    def test_returns_None_if_value_is_None(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        value = None
        rv = c.validate(value)
        assert rv is None

    def test_returns_empty_list_if_value_is_emtpy_list(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        value = []
        rv = c.validate(value)
        assert rv==[]

    def test_processes_all_items_if_no_qualifier(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        c.apply_to()
        value = ['a', 'b', 'c']
        rv = c.validate(value)
        assert rv[0]=='<u><i><b>a</b></i></u>'
        assert rv[1]=='<u><i><b>b</b></i></u>'
        assert rv[2]=='<u><i><b>c</b></i></u>'

    def test_integer_qualifiers_register(self):
        c = contexts.ArrayItemsContext()
        c.apply_to(0, 1, 3, 3, 1, 0, 1)
        assert c.qualifiers.qualifiers['index']=={0, 1, 3}

    def test_iterable_qualifiers_register(self):
        c = contexts.ArrayItemsContext()
        c.apply_to(1, 3, list(range(4, 9)))
        assert c.qualifiers.qualifiers['index']=={1, 3, 4, 5, 6, 7, 8}

    @pytest.mark.skip
    def test_callable_qualifiers_register(self):
        assert 0

    def test_processes_only_qualified_items(self, tags):
        c = contexts.ArrayItemsContext(*tags)
        c.apply_to(0, 2, list(range(7,9)))
        value = list('abcdefghij')
        rv = c.validate(value)
        assert rv==['<u><i><b>a</b></i></u>', 'b', '<u><i><b>c</b></i></u>',
            'd', 'e', 'f', 'g', '<u><i><b>h</b></i></u>', 
            '<u><i><b>i</b></i></u>', 'j']

    @pytest.mark.skip
    def test_can_qualify_a_single_item(self):
        assert False

    @pytest.mark.skip
    def test_can_have_multiple_qualifiers(self):
        assert False
