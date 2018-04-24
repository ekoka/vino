import pytest
from vino import errors as err
from vino.processors import runners

@pytest.fixture
def e_stack(): 
    rv = err.ValidationErrorStack('Stack of errors')
    for i in range(5):
        try:
            raise err.ValidationError('error '+str(i))
        except err.ValidationError as e:
            rv.append(e)
    return rv

class TestValidationError:

    def test_has_interrupt_validation_attribute(self):
        try:
            raise err.ValidationError('test')
        except err.ValidationError as e:
            assert hasattr(e,'interrupt_validation')

class TestValidationErrorStack:
    def test_acts_like_list_on_append(self, e_stack):
        assert len(e_stack.errors)==5

    def test_acts_like_list_on_len(self, e_stack):
        assert len(e_stack)==5

    def test_acts_is_indexable(self, e_stack):
        e = e_stack[0]
        assert isinstance(e, err.ValidationError)
        with pytest.raises(IndexError) as e:
            e = e_stack[5]

    def test_contains_all_errors_raised_by_stack(self, tags, fails_continue):
        processors = []
        for t, f in list(zip(tags, fails_continue)): 
            processors += t,f
        processors = tuple((p, None) for p in processors)
        rs = runners.RunnerStack(None, *processors)
        with pytest.raises(err.ValidationErrorStack) as es:
            rs.run('some value')
            assert len(es.value)==len(fails_continue)

    def test_errors_each_have_value_at_failure_time(self, tags, fails_continue):
        processors = []
        for t, f in list(zip(tags, fails_continue)): 
            processors += t,f
        processors = tuple((p, None) for p in processors)
        rs = runners.RunnerStack(None, *processors)
        with pytest.raises(err.ValidationErrorStack) as es:
            rs.run('some value')
            e = es.value
            assert e[0].data=='<b>some value</b>'
            assert e[1].data=='<i><b>some value</b></i>'
            assert e[2].data=='<u><i><b>some value</b></i></u>'

    def test_empty_flag_true_if_has_errors(self):
        stack = err.ValidationErrorStack('stack')
        assert stack.empty
        stack.append(err.ValidationError('new error'))
        assert not stack.empty
        e = stack.pop()
        assert stack.empty

    def test_can_be_cleared(self):
        stack = err.ValidationErrorStack('stack')
        stack.append(err.ValidationError('new error'))
        assert not stack.empty
        stack.clear()
        assert stack.empty

    @pytest.mark.skip
    def test_when_treated_as_exception_proxies_to_first_error(self):
        assert 0

@pytest.mark.skip
def test_error_raised_with_interrupt_should_also_set_it_on_error_stack():
    assert 0

