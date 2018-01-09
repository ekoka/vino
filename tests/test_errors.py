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
        processes = []
        for t, f in list(zip(tags, fails_continue)): 
            processes += t,f
        rs = runners.RunnerStack(None, *processes)
        try:
            rs.run('some value')
        except err.ValidationErrorStack as es:
            assert len(es)==len(fails_continue)

    def test_errors_each_have_value_at_failure_time(self, tags, fails_continue):
        processes = []
        for t, f in list(zip(tags, fails_continue)): 
            processes += t,f
        rs = runners.RunnerStack(None, *processes)
        try:
            rs.run('some value')
        except err.ValidationErrorStack as es:
            assert es[0].value=='<b>some value</b>'
            assert es[1].value=='<i><b>some value</b></i>'
            assert es[2].value=='<u><i><b>some value</b></i></u>'

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
