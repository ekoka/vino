import random
from vino.processors import runners
from vino import errors as err
from vino import contexts as ctx
from vino import qualifiers as quals
import pytest

class TestRunner:
    def test_run_method_returns_processor_value(s, randstr):
        # function
        processor = lambda v,c: v
        r = runners.Runner(processor)
        assert r.run(randstr)==randstr
        # object
        class p: 
            def run(self, data, context): return data
        processor = p()
        r = runners.Runner(processor)
        assert r.run(randstr)==randstr

    def test_tries_calling_vino_init_on_processor_registration(s,mocker):
        mk = mocker.MagicMock()
        r = runners.Runner(mk)
        assert mk.vino_init.called

    def test_tries_calling_run_method_on_processor(s, mocker):
        mk = mocker.MagicMock()
        mk.vino_init.return_value = mk
        r = runners.Runner(mk)
        r.run('x')
        assert mk.run.called

    def test_invokes_magic__call__after_run_call_fails(s, mocker):
        mk = mocker.MagicMock(spec=[]) # restraining the API
        r = runners.Runner(mk)
        r.run('x')
        assert mk.called

    def test_if_processor_has_run_method_Runner_wraps_with_function(s):
        class x:
            was_called = False
            def run(self): 
                self.was_called = True
                return 'abc'

        x_inst = x()
        r = runners.Runner(x_inst)
        assert x_inst.was_called is False
        assert r.processor() == 'abc'
        assert r.processor is not x_inst
        assert x_inst.was_called is True

    @pytest.mark.skip
    def test_Runner_calls_fail_function_on_processor_if_set(s):
        assert 0

class TestRunnerStack:

    def test_init_method_takes_context_as_first_param(self):
        with pytest.raises(TypeError) as exc_info:
            rs = runners.RunnerStack()
            assert ("missing 1 required positional argument: 'context'" 
                in str(exc_info.value))
        rs = runners.RunnerStack(None) 
        assert rs.context is None
        context = "bla"
        rs = runners.RunnerStack(context) 
        assert rs.context is context

    def test__init__proxies_to_add_method(self, tags, mocker):
        processors = tuple((t, None) for t in tags)
        add_mock = mocker.patch.object(runners.RunnerStack, 'add')
        rs = runners.RunnerStack(None, *processors) 
        add_mock.assert_called_once_with(*processors)

    def test_can_add_processors_in_tuple(self, tags):
        processors = ((t, None) for t in tags)
        rs = runners.RunnerStack(None)
        rs.add(*processors)
        assert len(rs)==len(tags)

    def test_cannot_add_processor_as_single_item(self, tags):
        rs = runners.RunnerStack(None)
        with pytest.raises(err.VinoError) as exc_info:
            rs.add(*tags)
        error = exc_info.value
        assert 'must be specified in tuples' in str(error).lower()

    def test_single_qfier_set_to_False_sets_runner_qfiers_to_False(s, tags):
        processors = [[t, None] for t in tags]
        processors[1][1] = False
        rs = runners.RunnerStack(None)
        rs.add(*processors)
        assert rs[1]['qualifiers'] is False
        
    def test_if_first_qfier_False_but_not_single_will_call_add_qualifiers(
            s, tags, mocker):
        processor = (tags[0], False, 3)
        rs = runners.RunnerStack(None)
        mk_add_qf = mocker.patch.object(rs, 'add_qualifiers')
        rs.add(processor)
        mk_add_qf.assert_called_once_with(False, 3)

    def test_if_single_qfier_is_None_no_qfiers_created(s, tags):
        processors = ((t, None) for t in tags)
        rs = runners.RunnerStack(None)
        rs.add(*processors)
        for r in rs:
            assert r['qualifiers'] is None

    def test_if_first_qfier_None_but_not_single_will_call_add_qualifiers(
            s, tags, mocker):
        processor = (tags[0], None, 3)
        rs = runners.RunnerStack(None)
        mk_add_qf = mocker.patch.object(rs, 'add_qualifiers')
        rs.add(processor)
        mk_add_qf.assert_called_once_with(None, 3)

    def test_returns_number_of_runners_on_len(s, processors):
        length = len(processors)
        stack = runners.RunnerStack(None, *processors)
        assert len(stack)==length

    def test_is_indexable(s, processors):
        length = len(processors)
        stack = runners.RunnerStack(None, *processors)
        for i in range(length):
            assert stack[i]

    def test_can_add_processors_without_qualifiers(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        rs = runners.RunnerStack(c)
        rs.add(*processors)
        assert len(rs)==3

    def test_can_add_processors_without_context(self, tags):
        processors = ((t, None) for t in tags)
        rs = runners.RunnerStack(None)
        rs.add(*processors)
        assert len(rs)==3

    def test_items_are_Runners(s, tags):
        processors = ((t, None) for t in tags)
        rs = runners.RunnerStack(None)
        rs.add(*processors)
        for r in rs:
            assert isinstance(r['runner'], runners.Runner)

    def test_cannot_add_qualifiers_without_runner_in_stack(self):
        rs = runners.RunnerStack(None)
        with pytest.raises(err.VinoError) as exc_info:
            assert len(rs)==0
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert 'without specifying a processor' in str(error).lower()

    def test_cannot_add_qualifiers_if_runner_has_qualifiers_set_to_False(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        c._qualifier_stack_constructor = quals.ItemQualifierStack
        rs = runners.RunnerStack(c)
        rs.add(*processors)
        rs[-1]['qualifiers'] = False
        with pytest.raises(err.VinoError) as exc_info:
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert 'does not accept qualifiers' in str(error).lower()

    def test_cannot_add_qualifier_without_context(self, tags):
        processors = ((t, None) for t in tags)
        rs = runners.RunnerStack(None)
        rs.add(*processors)
        with pytest.raises(err.VinoError) as exc_info:
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert 'must be given a context' in str(error).lower()

    def test_cant_add_qualifier_if_context_has_no_QStack_class(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        c._qualifier_stack_constructor = quals.ItemQualifierStack
        rs = runners.RunnerStack(c)
        rs.add(*processors)
        c._qualifier_stack_constructor = None
        with pytest.raises(err.VinoError) as exc_info:
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert ('qualifierstack constructor must be specified' 
                in str(error).lower())

    def test_can_add_qualifiers_if_context_has_QStack_class(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        c._qualifier_stack_constructor = quals.ItemQualifierStack
        rs = runners.RunnerStack(c)
        rs.add(*processors)
        rs.add_qualifiers([0,1])
        qstack = rs[-1]['qualifiers']
        qualifiers = qstack.qualifiers
        assert qualifiers['indexes']=={0,1}

    def test_successive_qualifier_applications_merges_qualifiers(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        c._qualifier_stack_constructor = quals.ItemQualifierStack
        rs = runners.RunnerStack(c)
        rs.add(*processors)
        rs.add_qualifiers([0,1])
        qstack = rs[-1]['qualifiers']
        qualifiers = qstack.qualifiers
        assert qualifiers['indexes']=={0,1}
        rs.add_qualifiers([1,3,8])
        assert qualifiers['indexes']=={0,1,3,8}
        rs.add_qualifiers(9,5,0,1)
        assert qualifiers['indexes']=={0,1,3,8,9,5}

    def test_run_method_returns_value(s, randstr):
        context = None
        processor = (lambda v,c: v), None
        rs = runners.RunnerStack(context, processor)
        assert rs.run(randstr)==randstr

    def test_executes_runners_in_fifo(s, tags):
        # tags are : bold, italic, and underline in that order
        processors = ((t, None) for t in tags)
        rs = runners.RunnerStack(None, *processors)
        post_process = '<u><i><b>'+'some contents'+'</b></i></u>'
        assert rs.run('some contents')==post_process

    def test_interrupts_validation_if_interrupt_flag_set_on_error(s, mocker):
        def failing_processor(value, context):
            e = err.ValidationError(
                "I'll fail you, no matter what", interrupt_validation=True)
            raise e
        #mk = mocker.MagicMock() # probably better to declare some specs 
        mk = mocker.MagicMock(spec=['run'])
        processors = tuple((t, None) for t in (failing_processor, mk))
        rs = runners.RunnerStack(None, *processors)
        try:
            value = rs.run('some contents')
        except err.ValidationErrorStack as e:
            assert not mk.run.called

    def test_calls_next_runner_if_interrupt_flag_not_set_on_error(s, mocker):
        def failing_processor(value, context):
            e = err.ValidationError(
                "I'll fail you, no matter what", interrupt_validation=False)
            raise e
        # we either need to specify spec to restrict the mock's public api 
        # or test for `mock.run.called`
        #mk = mocker.MagicMock() # probably better to declare some specs 
        mk = mocker.MagicMock(spec=['run', 'vino_init']) 
        mk.vino_init.return_value = mk
        processors = tuple((t, None) for t in [failing_processor, mk])
        rs = runners.RunnerStack(None, *processors)
        try:
            value = rs.run('some contents')
        except err.ValidationErrorStack as e:
            assert mk.run.called

    def test_run_assigns_failing_value_to_error_after_validation(s, tags):
        # tags are : bold, italic, and underline in that order
        def failing_processor(value, context):
            e = err.ValidationError("I'll fail you, no matter what", 
                                interrupt_validation=True)
            raise e
        processors = list((t, None) for t in tags)
        processors[1:1] = [(failing_processor, None)] # inserting at position 1
        rs = runners.RunnerStack(None, *processors)
        try:
            value = rs.run('some contents')
        except err.ValidationErrorStack as e:
            assert e[0].data=='<b>'+'some contents'+'</b>'

    def test_error_stack_given_last_value_before_interruption(s, tags):
        # tags are : bold, italic, and underline in that order
        def failing_processor(value, context):
            e = err.ValidationError("I'll fail you, no matter what", 
                                interrupt_validation=True)
            raise e
        processors = list((t, None) for t in tags)
        processors[1:1] = [[failing_processor, None]] # inserting at position 1
        rs = runners.RunnerStack(None, *processors)
        with pytest.raises(err.ValidationErrorStack) as e: 
            value = rs.run('some contents')
        assert e.value.data=='<b>'+'some contents'+'</b>'

    def test_error_stack_given_final_value_if_no_interruption(s, tags):
        # tags are : bold, italic, and underline in that order
        def failing_processor(value, context):
            e = err.ValidationError("I'll fail you, no matter what", 
                                interrupt_validation=False)
            raise e
        processors = list((t, None) for t in tags)
        processors[1:1] = [[failing_processor, None]] # inserting at position 1
        rs = runners.RunnerStack(None, *processors)
        with pytest.raises(err.ValidationErrorStack) as e: 
            value = rs.run('some contents')
        assert e.value.data=='<u><i><b>'+'some contents'+'</b></i></u>'


    @pytest.mark.skip
    def test_error_raised_in_qualifier_run_should_propagate_to_runner_stack():
        assert 0
