import pytest

@pytest.mark.skip
def test_error_raised_in_qualifier_run_should_propagate():
    assert 0

@pytest.mark.skip
def test_takes_state(): assert 0

#@pytest.mark.skip
#class TestArrayItemContext:
#
#    def test_can_contain_processors(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        assert len(c._runners)==len(tags)
#
#    def test_after_validate_array_has_same_length(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        value = ['a']
#        rv = c.validate(value)
#        assert len(rv)==len(value)
#
#    def test_validate_first_array_item(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        value = ['a']
#        rv = c.validate(value)
#        assert rv[0]=='<u><i><b>a</b></i></u>'
#
#    def test_validate_multiple_array_items(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        value = ['a', 'b', 'c']
#        rv = c.validate(value)
#        assert rv[0]=='<u><i><b>a</b></i></u>'
#        assert rv[1]=='<u><i><b>b</b></i></u>'
#        assert rv[2]=='<u><i><b>c</b></i></u>'
#
#    def test_returns_None_if_value_is_None(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        value = None
#        rv = c.validate(value)
#        assert rv is None
#
#    def test_returns_empty_list_if_value_is_emtpy_list(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        value = []
#        rv = c.validate(value)
#        assert rv==[]
#
#    def test_processes_all_items_if_no_qualifier(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        c.apply_to()
#        value = ['a', 'b', 'c']
#        rv = c.validate(value)
#        assert rv[0]=='<u><i><b>a</b></i></u>'
#        assert rv[1]=='<u><i><b>b</b></i></u>'
#        assert rv[2]=='<u><i><b>c</b></i></u>'
#
#    def test_integer_qualifiers_register(self):
#        c = contexts.ArrayItemsContext()
#        c.apply_to(0, 1, 3, 3, 1, 0, 1)
#        assert c.qualifiers.qualifiers['index']=={0, 1, 3}
#
#    def test_iterable_qualifiers_register(self):
#        c = contexts.ArrayItemsContext()
#        c.apply_to(1, 3, list(range(4, 9)))
#        assert c.qualifiers.qualifiers['index']=={1, 3, 4, 5, 6, 7, 8}
#
#    @pytest.mark.skip
#    def test_callable_qualifiers_register(self):
#        assert 0
#
#    def test_processes_only_qualified_items(self, tags):
#        c = contexts.ArrayItemsContext(*tags)
#        c.apply_to(0, 2, list(range(7,9)))
#        value = list('abcdefghij')
#        rv = c.validate(value)
#        assert rv==['<u><i><b>a</b></i></u>', 'b', '<u><i><b>c</b></i></u>',
#            'd', 'e', 'f', 'g', '<u><i><b>h</b></i></u>', 
#            '<u><i><b>i</b></i></u>', 'j']
#
#    @pytest.mark.skip
#    def test_can_qualify_a_single_item(self):
#        assert 0
#
#    @pytest.mark.skip
#    def test_can_have_multiple_qualifiers(self):
#        assert 0
#
#    @pytest.mark.skip
#    def test_items_are_processed_by_index_not_by_qualifiers_orders():
#        assert 0
