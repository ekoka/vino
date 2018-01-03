from vino import contexts
from vino.processors.runners import RunnerStack
import pytest

@pytest.fixture
def context():
    class rv(contexts.VinoContext): pass
    return rv

def test_RunnerStack_returns_number_of_runners_on_len():
    length = 5
    processors = [lambda: None for i in range(length)]
    stack = RunnerStack(None, *processors)
    assert len(stack)==length

def test_RunnerStack_is_indexable():
    length = 5
    def create_fnc(i):
        return lambda: i
    processors = [create_fnc(i) for i in range(length)]
    stack = RunnerStack(None, *processors)
    for i in range(length):
        assert stack[i].processor()==i

def test_context_created_without_processor_has_only_one_runner(context):
    c = context()
    assert len(c._runners)==1

#def test_first_processor_of_context_is_context(context):
#    c = context()
#    assert c._runners[0].processor is c
