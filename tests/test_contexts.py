from vino import contexts
from vino.processors import runners
from vino.processors import processors as proc
import pytest

@pytest.fixture
def context():
    class rv(contexts.VinoContext): pass
    return rv

def test_RunnerStack_returns_number_of_runners_on_len(processors):
    length = len(processors)
    stack = runners.RunnerStack(None, *processors)
    assert len(stack)==length

def test_RunnerStack_is_indexable(processors):
    length = len(processors)
    stack = runners.RunnerStack(None, *processors)
    for i in range(length):
        assert stack[i]

def test_RunnerStack_items_are_Runners(processors):
    length = len(processors)
    stack = runners.RunnerStack(None, *processors)
    for i in range(length):
        assert isinstance(stack[i], runners.Runner)

def test_context_created_without_processor_has_only_one_runner(context):
    c = context()
    assert len(c._runners)==1

def test_if_processor_has_run_method_Runner_wraps_with_function():
    class x:
        was_called = False
        def run(self): 
            self.was_called = True
            return 'abc'

    x_inst = x()
    r = runners.ProcessorRunner(x_inst)
    assert x_inst.was_called is False
    assert r.processor() == 'abc'
    assert r.processor is not x_inst
    assert x_inst.was_called is True
    
def test_first_runner_in_context_wraps_context_run_method(context, processors):
    context.run = lambda*a,**kw: 'abc'
    c = context(*processors)
    assert c._runners[0].processor() == 'abc'

def test_basic_context_can_validate_basic_types():
    b = contexts.BasicContext()
    r = b.validate(1)
    assert r==1

@pytest.mark.xfail
def test_basic_context_can_fail_non_basic_types():
    assert 0

@pytest.mark.xfail
def test_ValidationError_has_interrupt_validation_attribute():
    assert 0

@pytest.mark.xfail
def test_ValidationErrorStack_acts_like_list_on_append():
    assert 0

@pytest.mark.xfail
def test_BasicContext_type_check_interrupts_validation_on_failure():
    assert 0

@pytest.mark.xfail
def test_runner_stack_interrupts_validation_if_flag_raised_on_error():
    assert 0
