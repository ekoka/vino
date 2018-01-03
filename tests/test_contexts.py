from vino import contexts
from vino.processors import runners
from vino.processors import processors as proc
import pytest

@pytest.fixture
def context():
    class rv(contexts.VinoContext): pass
    return rv

@pytest.fixture
def processors():
    length = 5
    def create_fnc(i):
        return lambda: i
    processors = [create_fnc(i) for i in range(length)]
    return processors


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
