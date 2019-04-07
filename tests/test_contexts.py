from vino import contexts as ctx
from vino import errors as err
from vino.api.schema import obj, prim
from vino.processors import processors as proc
import pytest

@pytest.fixture
def diagnostic_proc():
    class C:
        def __init__(self, cb):
            self.cb = cb 

        def run(self, data, state):
            #self.matches = state['matches']
            self.cb(data, state) 
    return C

class TestContext:

    def test_empty_context_has_no_runner(self, context):
        c = context()
        assert len(c._runners)==0

    def test___init__takes_qualifiers_stack_cls_kwarg(s, context):
        c = context(qualifier_stack_cls=True)
        assert c.qualifier_stack_cls is True

    def test___init__takes_runner_stack_cls_kwarg(s, context, mocker):
        c = context(runner_stack_cls=mocker.MagicMock())
        assert c.runner_stack_cls.called

    def test__init__proxies_to_expand_method(s, context, tags, mocker):
        mk_expand = mocker.patch.object(context, 'expand')
        c = context(*tags)
        mk_expand.assert_called_once_with(*tags)

    def test_processors_given_proper_signature_if_received_as_is(
            s, tags, context, mocker):
        c = context()
        mk_add = mocker.patch.object(c._runners, 'add')
        c.expand(*tags)
        processors = tuple((t, None) for t in tags)
        mk_add.assert_called_once_with(*processors)

    def test_processors_given_proper_signature_if_received_as_tuples(
            s, tags, context, mocker):
        processors = tuple((t, None, 3, 2, False) for t in tags)
        c = context()
        mk_add = mocker.patch.object(c._runners, 'add')
        c.expand(*processors)
        mk_add.assert_called_once_with(*processors)

    def test_processors_added_to_runner_stack(s, tags, context):
        c = context()
        c.expand(*tags)
        assert len(c.runners)==len(tags)

    def test_validate_proxies_to_run(s, mocker, context):
        c = context()
        mk_run = mocker.patch.object(c, 'run')
        c.validate('abc')
        mk_run.assert_called_once_with('abc', c)

    def test_validate_method_does_not_take_context_object(s, context):
        c = context()
        # no context, all is good
        c.validate('abc')
        # context given, should raise
        with pytest.raises(TypeError) as e:
            c.validate('abc', 'context')
        assert ('2 positional arguments but 3 were given' 
                in str(e.value).lower())

    def test_run_method_takes_context_object_as_second_argument(s, context):
        c = context()
        # context passed, all is good
        c.run('abc', 'context')
        # no context, should raise
        with pytest.raises(TypeError) as e:
            c.run('abc')
        assert ("missing 1 required positional argument: 'context'" 
                in str(e.value).lower())

    def test_validate_passes_self_as_context_to_run_method(s, context, mocker):
        c = context()
        mk_run = mocker.patch.object(c, 'run')
        c.validate('abc')
        mk_run.assert_called_once_with('abc', c)

    def test_run_method_calls_runner_stack_run_method(s, context, mocker):
        c = context()
        mk_run = mocker.patch.object(c._runners, 'run')
        c.run('abc', c)
        mk_run.assert_called_once_with('abc')

    def test_apply_to_method_returns_context_with_qualifiers(
            s, context):
        c = context()
        rv = c.apply_to('abc', 'def')
        assert rv==(c, 'abc', 'def')

    # NOTE: functional test?
    def test_validation_continues_if_interrupt_flag_not_raised(s, tags):
        # tags are : bold, italic, and underline in that order
        def failing_processor(value, state):
            e = err.ValidationError("I'll fail you, no matter what", 
                                interrupt_validation=False)
            raise e
        processors = (failing_processor,) + tags
        try:
            c = ctx.Context(*processors)
            value = c.validate('some contents')
        except err.ValidationErrorStack as e:
            assert e.data=='<u><i><b>'+'some contents'+'</b></i></u>'

    @pytest.mark.skip
    def test_can_have_multiple_sub_contexts(s):
        assert 0 

    def test_spawned_context_is_different_than_original(
            s, tags, context):
        c = context(*tags)
        nc = c.spawn()
        assert nc is not c

    def test_spawned_context_has_same_constructor_than_original(
            s, context, tags):
        c = context(*tags)
        nc = c.spawn()
        assert nc.__class__ is c.__class__

    def test_spawned_context_has_different_runner_stack_than_original(
            s, tags, context):
        c = context(*tags)
        nc = c.spawn()
        assert c._runners is not nc._runners

    def test_spawned_context_runner_stack_refers_to_spawned_context(
            s, tags, context):
        c = context(*tags)
        nc = c.spawn()
        assert nc.runners.context is nc
        
    def test_spawned_context_runner_stack_received_same_runners_as_original(
            s, tags, context):
        c = context(*tags)
        nc = c.spawn()
        for i,r in enumerate(c.runners):
            assert r is nc.runners[i]

    def test_add_method_does_not_change_current_context(s, tags, context):
        c = context(*tags)
        count = len(c.runners)
        runners = c.runners
        stack = c.runners[:]
        c.add(lambda*a:None)
        for i, r in enumerate(c.runners):
            assert r==stack[i]
        assert len(c.runners)==count
        assert runners==c.runners

    def test_add_method_spawns_another_context(s, tags, context):
        c = context(*tags)
        nc = c.add(lambda*a:None)
        assert nc is not c

    def test_add_method_without_processors_simply_spawns_new_context(
            s, tags, context):
        c = context(*tags)
        nc = c.add()
        assert nc is not c

    def test_add_method_with_processors_spawns_context_with_more_processors(
            s, tags, context):
        c = context(*tags)
        nc = c.add(*tags)
        assert len(nc.runners)==len(c.runners) + len(tags)

    def test_object_context(context, diagnostic_proc, logger):
        proclist = [lambda x=x, *a,**kw: 'abc' for x in range(5)]
        def run(data, state):
            logger.info(data) 
            logger.info(state) 

        proc = diagnostic_proc(run) 
        c = obj(
            prim().apply_to('a', 'c'),
            #prim().apply_to('b', 'a'),
            #prim().apply_to('c', 'd'),
            proc, 
           #p[3]().apply_to('d'),
           #p[4]().apply_to('e'),
        )
        # qualifier stack
        qs = c.runners[2]['qualifiers']
        assert qs._qualifiers['keys']==set(['a', 'c'])
        c.validate({
            'a': 'bec',
            'b': 'bec',
            'c': 'bec',
            'd': 'bec',
            'e': 'bec',
            'f': 'bec',
            'g': 'bec',
        })


