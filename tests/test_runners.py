import random
from vino.processors import runners
from vino import errors as err
from vino import contexts
import pytest

class TestRunner:
    def test_run_method_returns_processor_value(s, randstr):
        # function
        processor = lambda v,c: v
        r = runners.ProcessorRunner(processor)
        assert r.run(randstr)==randstr
        # object
        class p: 
            def run(self, data, context): return data
        processor = p()
        r = runners.ProcessorRunner(processor)
        assert r.run(randstr)==randstr

    def test_tries_calling_vino_init_on_processor_registration(s,mocker):
        mk = mocker.MagicMock()
        r = runners.ProcessorRunner(mk)
        assert mk.vino_init.called

    def test_tries_calling_run_method_on_processor(s, mocker):
        mk = mocker.MagicMock()
        mk.vino_init.return_value = mk
        r = runners.ProcessorRunner(mk)
        r.run('x')
        assert mk.run.called

    def test_invokes_magic__call__after_run_call_fails(s, mocker):
        mk = mocker.MagicMock(spec=[]) # restraining the API
        r = runners.ProcessorRunner(mk)
        r.run('x')
        assert mk.called

    def test_if_processor_has_run_method_Runner_wraps_with_function(s):
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
    def test_Runner_calls_fail_function_on_processor_if_set(s):
        assert 0

class TestRunnerStack:
    def test_run_method_returns_value(s, randstr):
        processor = lambda v,c: v
        rs = runners.RunnerStack(None, processor)
        assert rs.run(randstr)==randstr

    def test_returns_number_of_runners_on_len(s, processors):
        length = len(processors)
        stack = runners.RunnerStack(None, *processors)
        assert len(stack)==length

    def test_is_indexable(s, processors):
        length = len(processors)
        stack = runners.RunnerStack(None, *processors)
        for i in range(length):
            assert stack[i]

    def test_items_are_Runners(s, processors):
        length = len(processors)
        stack = runners.RunnerStack(None, *processors)
        for i in range(length):
            assert isinstance(stack[i], runners.Runner)

    def test_rejects_named_processor_outside_object_context(s):
        class P:
            def run(s, v): return v
        p = P()
        p.name = 'whatever'
        with pytest.raises(err.VinoError) as exc_info:
            rs = runners.RunnerStack(None, p)
        error = exc_info.value
        assert 'context enclosing' in str(error).lower()
        assert isinstance(error, err.VinoError)

    def test_accepts_named_processor_within_object_context(s):
        class P:
            def run(s, v): return v
        p = P()
        p.name = 'whatever'
        c = contexts.ObjectContext(p)
        assert len(c._runners)==2

@pytest.mark.skip
def test_indexed_processor_or_context_outside_array_raises_error():
    # for RunnerStack
    assert 0

@pytest.mark.skip
def test_named_processor_or_context_outside_object_raises_error():
    # for RunnerStack
    assert 0

