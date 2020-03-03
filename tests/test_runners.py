import random
from collections import namedtuple
import pytest

from vino.processors import runners
from vino.processors.runners import Runner, RunnerStack
from vino import errors as err
from vino import contexts as ctx
from vino import qualifiers as quals

class TestRunner:

    def test_callable_processor_should_register(s):
        """Runner(proc)
        if proc is callable, should register it
        """
        class P: 
            def __call__(self, data, state):
                return data
        processor = P()
        r = Runner(processor)
        assert hasattr(r, 'processor')

    def test_processor_with_run_method_should_register(s):
        """Runner(proc)
        if proc has run() method, should register it
        """
        class P: 
            def run(self, data, state):
                return data
        processor = P()
        r = Runner(processor)
        assert hasattr(r, 'processor')

    def test_processor_not_callable_with_no_run_method_should_be_rejected(s):
        """Runner(p)
        if p not callable and has no run() method, should not register it
        """
        class P:
            def execute(self, data, state): 
                return 'abc'
        p = P() 
        with pytest.raises(err.VinoError) as e:
            r = Runner(p)
        assert 'invalid processor' in str(e.value).lower()

    def test_if_processor_has_vino_init_should_call_it(s,mocker):
        """ Runner(p)
        if p has vino_init(), should call it
        """
        mk = mocker.Mock(spec=['vino_init', 'run'])
        r = Runner(mk)
        assert mk.vino_init.called

    def test_get_processor_proxy_should_return_ProcProxy_object(s):
        """pp = get_processor_proxy(proc)
        if proc valid processor, pp should be a ProcProxy instance
        """
        class P1: 
            def run(self, data, state):
                return data
        p1 = P1()
        class P2:
            def __call__(self, data, state):
                return data
        p2 = P2()
        pp1 = Runner.get_processor_proxy(p1)
        pp2 = Runner.get_processor_proxy(p2)
        assert isinstance(pp1, Runner.ProcProxy)
        assert isinstance(pp2, Runner.ProcProxy)

    def test_procproxy_object_should_have_4_attributes(s):
        """pp = get_processor_proxy(p)
        pp should have 4 attributes
        """
        class P: 
            def run(self, data, state):
                return data
        processor1 = P()
        processor2 = lambda d,s: d
        for p in (processor1, processor2):
            pp = Runner.get_processor_proxy(p)
            assert hasattr(pp, 'default')
            assert hasattr(pp, 'override')
            assert hasattr(pp, 'failsafe')
            assert hasattr(pp, 'raw_processor')

    def test_procproxy_override_should_default_to_None(s):
        """pp = get_processor_proxy(p)
        pp.override should default to None
        """
        class P: 
            def run(self, data, state):
                return data
        processor1 = P()
        processor2 = lambda d,s: d
        for p in (processor1, processor2):
            pp = Runner.get_processor_proxy(p)
            assert pp.override is None

    def test_procproxy_default_should_default_to_None(s):
        """pp = get_processor_proxy(p)
        pp.default should default to None
        """
        class P: 
            def run(self, data, state):
                return data
        processor1 = P()
        processor2 = lambda d,s: d
        for p in (processor1, processor2):
            pp = Runner.get_processor_proxy(p)
            assert pp.default is None

    def test_procproxy_failsafe_should_default_to_None(s):
        """pp = get_processor_proxy(p)
        pp.failsafe should default to None
        """
        class P: 
            def run(self, data, state):
                return data
        processor1 = P()
        processor2 = lambda d,s: d
        for p in (processor1, processor2):
            pp = Runner.get_processor_proxy(p)
            assert pp.failsafe is None
        
    def test_if_proc_callable_procproxy_run_should_refer_to_proc(s):
        """pp = get_processor_proxy(proc)
        if proc is callable, pp.run should be a reference to proc
        """
        class P: 
            def __call__(self, data, state):
                return data
        p = P()
        pp = Runner.get_processor_proxy(p)
        assert pp.run is p

    def test_if_proc_has_run_procproxy_run_should_refer_to_proc_run(s):
        """pp = get_processor_proxy(proc)
        if proc.run is callable, pp.run should be a reference to proc.run
        """
        class P: 
            def run(self, data, state):
                return data
        p = P()
        pp = Runner.get_processor_proxy(p)
        # because of descriptor protocol we use equality rather than identity
        assert pp.run==p.run 

    def test_procproxy_raw_processor_should_refer_to_original_proc(s): 
        """pp = get_processor_proxy(proc)
        pp.raw_processor should be proc"""
        class P1: 
            def run(self, data, state):
                return data
        p1 = P1()
        class P2:
            def __call__(self, data, state):
                return data
        p2 = P2()
        p3 = lambda d,s: d
        for p in (p1,p2,p3):
            pp = Runner.get_processor_proxy(p)
            assert pp.raw_processor is p

    def test_run_successfully_should_return_processor_rv(s, randstr):
        '''result = run(value)
        if no contingency intervenes, result should be processor's rv'''
        processor = lambda d,s: d*3
        r = Runner(processor)
        assert r.run(randstr)==processor(randstr, None)

    # ------ override batch

    def test_run_should_call_run_override_first_if_procproxy_override_set(
            s, mocker):
        """run()
        if processor.override is set, should call run_override() first
        """
        proc = mocker.Mock(spec=['override', 'run', 'default', 'failsafe'])
        def override(*a, **kw): 
            raise Exception('override called first')
        def default(*a, **kw): 
            raise Exception('default called first')
        def failsafe(*a, **kw): 
            raise Exception('failsafe called first')
        proc.override = [override]
        proc.default = [default]
        proc.failsafe = [failsafe]
        r = Runner(proc)
        with pytest.raises(Exception) as e: 
            r.run()
        assert 'override called first' in str(e.value)

    # -------- default batch

    def test_run_should_call_run_default_if_procproxy_default_set(
            s, mocker, logger):
        """run()
        if data missing and processor.default set, should call run_default()
        """
        def proc(data, state):
            return data
        proc.default = mocker.Mock()
        r = Runner(proc)
        mk_run_default = mocker.patch.object(r, 'run_default', 
                                             return_value='abc')
        r.run()
        assert mk_run_default.called

    def test_run_should_not_call_run_default_if_data_not_missing(s, mocker):
        """run(data)
        if data is not missing, should not call run_default()
        """
        def proc(data, state):
            return data
        d = mocker.Mock(return_value='abc')
        proc.default = [d]
        r = Runner(proc)
        r.run(data=None)
        assert not d.called

    def test_run_should_still_call_procproxy_run_after_run_default(
            s, mocker, logger):
        """run()
        if run_default called, should still call ProcProxy.run()
        """
        proc = lambda *a,**k: 123
        proc.default = [lambda *a,**k: 'abc']
        r = Runner(proc)
        run_default = mocker.patch.object(r, 'run_default')
        procproxy = mocker.patch.object(r, 'processor')
        r.run()
        assert run_default.called
        assert procproxy.run.called

    # ------- failsafe

    def test_run_should_call_save_or_fail_if_processor_fails(
            s, mocker):
        """run()
        if ProcProxy.run() fails, should call save_or_fail()
        """
        def proc(data, state):
            raise err.ValidationError('failure')
        proc.failsafe = [lambda *a,**k:'abc']
        r = Runner(proc)
        mk_save_or_fail = mocker.patch.object(r, 'save_or_fail')
        r.run()
        assert mk_save_or_fail.called

    def test_run_should_not_call_save_or_fail_if_processor_succeeds(s, mocker):
        """run()
        if processor succeeds, should not call save_or_fail()
        """
        def proc(data, state):
            return 123
        proc.failsafe = [lambda *a,**k:'abc']
        r = Runner(proc)
        mk_save_or_fail = mocker.patch.object(r, 'save_or_fail')
        assert r.run()==123
        assert not mk_save_or_fail.called

    def test_run_failsafe_should_run_failsafe_funcs_in_a_batch(s):
        """rv = run_failsafe(failsafe, data)
        rv should be result of batch calls to failsafe functions
        """
        failsafe = [lambda data,state: (data+'c'), lambda data,state: (data*3)]
        r = Runner(lambda*a,**k:None)
        assert r.run_failsafe(failsafe, 'ab')=='abcabcabc'

    def test_run_default_should_run_default_funcs_in_a_batch(s):
        """rv = run_default(default, data)
        rv should be result of batch calls to default functions
        """
        default = [lambda data,state: (data+'c'), lambda data,state: (data*3)]
        r = Runner(lambda*a,**k:None)
        assert r.run_default(default, 'ab')=='abcabcabc'

    def test_run_override_should_run_override_funcs_in_a_batch(s):
        """rv = run_override(override, data)
        rv should be result of batch calls to override functions
        """
        override = [lambda data,state: (data+'c'), lambda data,state: (data*3)]
        r = Runner(lambda*a,**k:None)
        assert r.run_override(override, 'ab')=='abcabcabc'

class TestRunnerStack:

    def test_init_method_takes_context_as_first_param(self):
        with pytest.raises(TypeError) as exc_info:
            rs = RunnerStack()
            assert ("missing 1 required positional argument: 'context'" 
                in str(exc_info.value))
        rs = RunnerStack(None) 
        assert rs.context is None
        context = "bla"
        rs = RunnerStack(context) 
        assert rs.context is context

    def test__init__proxies_to_add_method(self, tags, mocker):
        processors = tuple((t, None) for t in tags)
        mk_add = mocker.patch.object(RunnerStack, 'add')
        rs = RunnerStack(None, *processors) 
        mk_add.assert_called_once_with(*processors)

    def test_can_add_processors_in_tuple(self, tags):
        processors = ((t, None) for t in tags)
        rs = RunnerStack(None)
        rs.add(*processors)
        assert len(rs)==len(tags)

    def test_cannot_add_processor_as_single_item(self, tags):
        rs = RunnerStack(None)
        with pytest.raises(err.VinoError) as exc_info:
            rs.add(*tags)
        error = exc_info.value
        assert 'must be specified in tuples' in str(error).lower()

    def test_single_qfier_set_to_False_sets_runner_qfiers_to_False(s, tags):
        processors = [[t, None] for t in tags]
        processors[1][1] = False
        rs = RunnerStack(None)
        rs.add(*processors)
        assert rs[1]['qualifiers'] is False
        
    def test_if_first_qfier_False_but_not_single_will_call_add_qualifiers(
            s, tags, mocker):
        processor = (tags[0], False, 3)
        rs = RunnerStack(None)
        mk_add_qf = mocker.patch.object(rs, 'add_qualifiers')
        rs.add(processor)
        mk_add_qf.assert_called_once_with(False, 3)

    def test_if_single_qfier_is_None_no_qfiers_created(s, tags):
        processors = ((t, None) for t in tags)
        rs = RunnerStack(None)
        rs.add(*processors)
        for r in rs:
            assert r['qualifiers'] is None

    def test_if_first_qfier_None_but_not_single_will_call_add_qualifiers(
            s, tags, mocker):
        processor = (tags[0], None, 3)
        rs = RunnerStack(None)
        mk_add_qf = mocker.patch.object(rs, 'add_qualifiers')
        rs.add(processor)
        mk_add_qf.assert_called_once_with(None, 3)

    def test_returns_number_of_runners_on_len(s, processors):
        length = len(processors)
        stack = RunnerStack(None, *processors)
        assert len(stack)==length

    def test_is_indexable(s, processors):
        length = len(processors)
        stack = RunnerStack(None, *processors)
        for i in range(length):
            assert stack[i]

    def test_can_add_processors_without_qualifiers(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        rs = RunnerStack(c)
        rs.add(*processors)
        assert len(rs)==3

    def test_can_add_processors_without_context(self, tags):
        processors = ((t, None) for t in tags)
        rs = RunnerStack(None)
        rs.add(*processors)
        assert len(rs)==3

    def test_items_are_Runners(s, tags):
        processors = ((t, None) for t in tags)
        rs = RunnerStack(None)
        rs.add(*processors)
        for r in rs:
            assert isinstance(r['runner'], Runner)

    def test_cannot_add_qualifiers_without_runner_in_stack(self):
        rs = RunnerStack(None)
        with pytest.raises(err.VinoError) as exc_info:
            assert len(rs)==0
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert 'without specifying a processor' in str(error).lower()

    def test_cannot_add_qualifiers_if_runner_has_qualifiers_set_to_False(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        c._qualifier_stack_constructor = quals.ItemQualifierStack
        rs = RunnerStack(c)
        rs.add(*processors)
        rs[-1]['qualifiers'] = False
        with pytest.raises(err.VinoError) as exc_info:
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert 'does not accept qualifiers' in str(error).lower()

    def test_cannot_add_qualifier_without_context(self, tags):
        processors = ((t, None) for t in tags)
        rs = RunnerStack(None)
        rs.add(*processors)
        with pytest.raises(err.VinoError) as exc_info:
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert 'must be given a context' in str(error).lower()

    def test_cannot_add_qualifier_if_context_has_no_QStack_class(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context(qualifier_stack_cls=quals.ItemQualifierStack)
        rs = RunnerStack(c)
        rs.add(*processors)
        c.qualifier_stack_cls = None
        with pytest.raises(err.VinoError) as exc_info:
            rs.add_qualifiers([0,1])
        error = exc_info.value
        assert ('qualifierstack constructor must be specified' 
                in str(error).lower())

    def test_can_add_qualifiers_if_context_has_QStack_class(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context()
        c = ctx.Context(qualifier_stack_cls=quals.ItemQualifierStack)
        rs = RunnerStack(c)
        rs.add(*processors)
        rs.add_qualifiers([0,1])
        qstack = rs[-1]['qualifiers']
        qualifiers = qstack.qualifiers
        assert qualifiers['indices']=={0,1}

    def test_successive_qualifier_applications_merges_qualifiers(self, tags):
        processors = ((t, None) for t in tags)
        c = ctx.Context(qualifier_stack_cls=quals.ItemQualifierStack)
        rs = RunnerStack(c)
        rs.add(*processors)
        rs.add_qualifiers([0,1])
        qstack = rs[-1]['qualifiers']
        qualifiers = qstack.qualifiers
        assert qualifiers['indices']=={0,1}
        rs.add_qualifiers([1,3,8])
        assert qualifiers['indices']=={0,1,3,8}
        rs.add_qualifiers(9,5,0,1)
        assert qualifiers['indices']=={0,1,3,8,9,5}

    def test_run_method_returns_value(s, randstr):
        context = None
        processor = (lambda v,c: v), None
        rs = RunnerStack(context, processor)
        assert rs.run(randstr)==randstr

    def test_executes_runners_in_fifo(s, tags):
        # tags are : bold, italic, and underline in that order
        processors = ((t, None) for t in tags)
        rs = RunnerStack(None, *processors)
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
        rs = RunnerStack(None, *processors)
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
        rs = RunnerStack(None, *processors)
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
        rs = RunnerStack(None, *processors)
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
        rs = RunnerStack(None, *processors)
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
        rs = RunnerStack(None, *processors)
        with pytest.raises(err.ValidationErrorStack) as e: 
            value = rs.run('some contents')
        assert e.value.data=='<u><i><b>'+'some contents'+'</b></i></u>'

    def test_copy_returns_different_runner_stack(s):
        rs = RunnerStack(None)
        nrs = rs.copy()
        assert rs is not nrs

    def test_copied_rs_has_same_runners_than_original(s, tags):
        processors = tuple((t,None) for t in tags)
        rs = RunnerStack(None, *processors)
        nrs = rs.copy()
        for i,r in enumerate(rs):
            assert r is nrs[i]

    def test_copied_rs_has_same_constructor_than_original(s, tags):
        processors = tuple((t,None) for t in tags)
        rs = RunnerStack(None, *processors)
        nrs = rs.copy()
        assert rs.__class__ is nrs.__class__

    def test_by_default_new_rs_has_same_ctx_as_original(s, tags):
        my_context = {'a':'b'}
        processors = tuple((t,None) for t in tags)
        rs = RunnerStack(my_context, *processors)
        nrs1 = rs.copy()
        nrs2 = rs.copy(None)
        assert rs.context is nrs1.context is nrs2.context

    def test_can_override_context_for_new_rs(s, tags):
        context1 = {'a':'b'}
        context2 = {'b':'a'}
        processors = tuple((t,None) for t in tags)
        rs = RunnerStack(context1, *processors)
        nrs = rs.copy(context2)
        assert nrs.context is context2

    def test_overriding_context_for_new_rs_does_not_change_original(s, tags):
        context1 = {'a':'b'}
        context2 = {'b':'a'}
        processors = tuple((t,None) for t in tags)
        rs = RunnerStack(context1, *processors)
        nrs = rs.copy(context2)
        assert rs.context is context1

    def test_can_set_context_to_None_for_new_rs_by_specifying_False(s, tags):
        context1 = {'a':'b'}
        processors = tuple((t,None) for t in tags)
        rs = RunnerStack(context1, *processors)
        nrs = rs.copy(False)
        assert nrs.context is None

    @pytest.mark.skip
    def test_error_raised_in_qualifier_run_should_propagate_to_runner_stack():
        assert 0


