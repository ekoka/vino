from vino import contexts
from vino import errors as err
from vino.processors import runners
from vino.processors import processors as proc
import pytest

@pytest.fixture
def context():
    class rv(contexts.VinoContext): pass
    return rv

def test_context_created_without_processor_has_only_one_runner(context):
    c = context()
    assert len(c._runners)==1

def test_first_runner_in_context_wraps_context_run_method(context, processors):
    context.run = lambda*a,**kw: 'abc'
    c = context(*processors)
    assert c._runners[0].processor() == 'abc'

def test_basic_context_with_no_added_processors_returns_value(randstr):
    b = contexts.BasicContext()
    assert b.validate(randstr)==randstr

def test_basic_context_can_validate_basic_type():
    b = contexts.BasicContext()
    b.validate(1)
    b.validate(1.2)
    b.validate(None)
    b.validate("")
    b.validate("(- . -)")
    b.validate(False)
    b.validate(True)

def test_basic_context_raises_ValidationError_on_invalid_basic_type():
    b = contexts.BasicContext()
    with pytest.raises(err.ValidationError) as exc:
        b.validate([])
    with pytest.raises(err.ValidationError) as exc:
        b.validate(list('abcdef'))
    with pytest.raises(err.ValidationError) as exc:
        b.validate({'a': 'e'})
    #TODO: what happens with byte type

def test_BasicContext_executes_all_validations_in_fifo(tags):
    # tags are : bold, italic, and underline in that order
    b = contexts.BasicContext(*tags)
    value = b.validate('some contents')
    assert value=='<u><i><b>'+'some contents'+'</b></i></u>'

def test_validation_continues_if_interrupt_flag_not_raised(tags):
    # tags are : bold, italic, and underline in that order
    def failing_processor(value, context):
        e = err.ValidationError("I'll fail you, no matter what", 
                            interrupt_validation=False)
        raise e
    processors = (failing_processor,) + tags
    try:
        b = contexts.BasicContext(*processors)
        value = b.validate('some contents')
    except err.ValidationErrorStack as e:
        assert e.value=='<u><i><b>'+'some contents'+'</b></i></u>'

def test_ValidationError_contains_failing_value_after_validation(tags):
    # tags are : bold, italic, and underline in that order
    def failing_processor(value, context):
        e = err.ValidationError("I'll fail you, no matter what", 
                            interrupt_validation=True)
        raise e
    processors = list(tags)
    processors[1:1] = [failing_processor] # inserting at position 1 
    try:
        b = contexts.BasicContext(*processors)
        value = b.validate('some contents')
    except err.ValidationErrorStack as e:
        assert e[0].value=='<b>'+'some contents'+'</b>'

def test_ValidationErrorStack_has_value_up_to_validation_interruption(tags):
    # tags are : bold, italic, and underline in that order
    def failing_processor(value, context):
        e = err.ValidationError("I'll fail you, no matter what", 
                            interrupt_validation=True)
        raise e
    processors = list(tags)
    processors[1:1] = [failing_processor] # inserting at position 1 
    try:
        b = contexts.BasicContext(*processors)
        value = b.validate('some contents')
    except err.ValidationErrorStack as e:
        assert e.value=='<b>'+'some contents'+'</b>'

def test_ValidationErrorStack_has_final_value_if_no_interruption(tags):
    # tags are : bold, italic, and underline in that order
    def failing_processor(value, context):
        e = err.ValidationError("I'll fail you, no matter what", 
                            interrupt_validation=False)
        raise e
    processors = list(tags)
    processors[1:1] = [failing_processor] # inserting at position 1 
    try:
        b = contexts.BasicContext(*processors)
        value = b.validate('some contents')
    except err.ValidationErrorStack as e:
        assert e.value=='<u><i><b>'+'some contents'+'</b></i></u>'

def test_validation_interrupted_if_flag_raised_on_error(mocker):
    def failing_processor(value, context):
        e = err.ValidationError(
            "I'll fail you, no matter what", interrupt_validation=True)
        raise e
    #mk = mocker.MagicMock(spec=[])
    mk = mocker.MagicMock()
    processors = [failing_processor, mk]
    try:
        b = contexts.BasicContext(*processors)
        value = b.validate('some contents')
    except err.ValidationErrorStack as e:
        assert not mk.run.called
        #mk.assert_not_called()

def test_validation_proceeds_if_flag_not_raised_on_error(mocker):
    def failing_processor(value, context):
        e = err.ValidationError(
            "I'll fail you, no matter what", interrupt_validation=False)
        raise e
    # we either need to specify spec to restrict the mock's public api 
    # or test for `mock.run.called`
    #mk = mocker.MagicMock(spec=[]) 
    mk = mocker.MagicMock() 
    mk.vino_init.return_value = mk
    processors = [failing_processor, mk]
    try:
        b = contexts.BasicContext(*processors)
        value = b.validate('some contents')
    except err.ValidationErrorStack as e:
        assert mk.run.called


     
