from vino import contexts as ctx
from vino import errors as err
import pytest

class TestContext:

    def test_empty_context_has_no_runner(self, context):
        c = context()
        assert len(c._runners)==0

    def test_has__qualifiers_stack_constructor_property(s, context):
        c = context
        assert hasattr(c, '_qualifier_stack_constructor')

    def test__init__proxies_to_add_method(s, context, tags, mocker):
        mock_add = mocker.patch.object(context, 'add')
        c = context(*tags)
        mock_add.assert_called_once_with(*tags)

    def test_can_add_processors_specified_in_tuple(s, tags, context, mocker):
        processors = ((t, None) for t in tags)
        c = context()
        mocker.patch.object(c, '_runners')
        c.add(*processors)

    def test_can_add_processors_specified_alone(s, tags, context, mocker):
        c = context()
        mocker.patch.object(c, '_runners')
        c.add(*tags)

    def test_tuples_added_to_runner_stack_with_proper_signature(
            s, tags, context, mocker):
        processors = ((t, None) for t in tags)
        c = context()
        r = mocker.patch.object(c, '_runners')
        c.add(*processors)
        r.add.assert_called_once_with(
            (tags[0], None), (tags[1], None), (tags[2], None))

    def test_tuples_added_to_runner_stack(s, tags, context):
        processors = ((t, None) for t in tags)
        c = context()
        c.add(*processors)
        assert len(c.runners)==len(tags)

    def test_processors_added_to_runner_stack_with_proper_signature(
            s, tags, context, mocker):
        c = context()
        r = mocker.patch.object(c, '_runners')
        c.add(*tags)
        r.add.assert_called_once_with(
            (tags[0], None), (tags[1], None), (tags[2], None))

    def test_processors_added_to_runner_stack(s, tags, context):
        c = context()
        c.add(*tags)
        assert len(c.runners)==len(tags)

    def test_validate_method_proxies_to_run_method(s, mocker, context):
        c = context()
        mock_run = mocker.patch.object(c, 'run')
        c.validate('abc')
        mock_run.assert_called_once_with('abc', c)

    def test_validate_method_does_not_take_context_object(s, context):
        c = context()
        # no context, all is good
        c.validate('abc')
        # context given, should raise
        with pytest.raises(TypeError) as exc_info:
            c.validate('abc', 'context')
        assert ('validate() takes 2 positional arguments' 
                in str(exc_info.value).lower())

    def test_run_method_takes_context_object_as_second_argument(s, context):
        c = context()
        # context passed, all is good
        c.run('abc', 'context')
        # no context, should raise
        with pytest.raises(TypeError) as exc_info:
            c.run('abc')
        assert ("missing 1 required positional argument: 'context'" 
                in str(exc_info.value).lower())

    def test_validate_passes_self_as_context_to_run_method(s, context, mocker):
        c = context()
        mock_run = mocker.patch.object(c, 'run')
        c.validate('abc')
        mock_run.assert_called_once_with('abc', c)

    def test_run_method_calls_runner_stack_run_method(s, context, mocker):
        c = context()
        mock_run = mocker.patch.object(c._runners, 'run')
        c.run('abc', c)
        mock_run.assert_called_once_with('abc')

    def test_apply_to_method_returns_context_with_qualifiers(
            s, context, mocker):
        c = context()
        rv = c.apply_to('abc', 'def')
        assert rv==(c, 'abc', 'def')

    # NOTE: functional test?
    def test_validation_continues_if_interrupt_flag_not_raised(s, tags):
        # tags are : bold, italic, and underline in that order
        def failing_processor(value, context):
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
    def test_can_have_multiple_sub_contexts():
        assert False
