import random
from vino.processors import runners
from vino import errors as err
import pytest

def test_Runner_run_method_returns_processor_value(randstr):
    # function
    processor = lambda v,c: v
    r = runners.ProcessorRunner(processor)
    assert r.run(randstr)==randstr
    # object
    class p: 
        def run(self, value, context): return value
    processor = p()
    r = runners.ProcessorRunner(processor)
    assert r.run(randstr)==randstr

def test_RunnerStack_run_method_returns_value(randstr):
    processor = lambda v,c: v
    rs = runners.RunnerStack(None, processor)
    assert rs.run(randstr)==randstr

def test_Runner_tries_to_call_vino_init_on_processor(mocker):
    mk = mocker.MagicMock()
    r = runners.ProcessorRunner(mk)
    assert mk.vino_init.called

def test_Runner_tries_calling_run_method_on_processor(mocker):
    mk = mocker.MagicMock()
    mk.vino_init.return_value = mk
    r = runners.ProcessorRunner(mk)
    r.run('x')
    assert mk.run.called

def test_Runner_calls_processor_after_run_method_call_fails(mocker):
    mk = mocker.MagicMock(spec=[]) # restraining the API
    r = runners.ProcessorRunner(mk)
    r.run('x')
    assert mk.called

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

@pytest.mark.skip
def test_Runner_calls_fail_function_on_processor_if_set():
    assert 0
