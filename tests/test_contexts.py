from vino import contexts
from vino.processors.runners import RunnerStack
import pytest

@pytest.fixture
def context():
    class rv(context.VinoContext): pass

def test_RunnerStack_returns_number_of_runners_on_len(logger):
    length = 5
    processors = [lambda: None for i in range(length)]
    stack = RunnerStack(None, *processors)
    assert len(stack)==length

#def test_context_created_without_processor_has_only_one_runner(context):
#    c = context()
#    assert len(c._runners)==1
