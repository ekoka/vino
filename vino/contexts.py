from .errors import VinoError, ValidationError, ValidationErrorStack
from .processors.runners import RunnerStack
from .utils import is_str

class VinoContext:
    ''' The Context represent the primary scope of influence of a processor.
    Basic JSON elements (number, string, boolean, null) have a single context,
    within which the processors declared can influence the data. Array and
    Object elements each have two scopes, one for the constructs themselves
    and one for their items or properties.
    '''
    def __init__(self, *processors, name=None): # name is a keyword-only argument
        self.name = name
        # prepend context to list of processors
        processors = [self] + processors
        self._runners = RunnerStack(self, *processors)

    def run(self, context, value):
        """ Let's quack like a Processor """
        # default behaviour is to simply return the value untouched
        return value


class BasicContext(VinoContext):
        
    def validate(self, value):
        errors = []
        result = None
        for f in self.processors:
            try:
                value = f.run(value)
            except ValidationError as e:
                if e.interrupt_validation: #  
                    raise e
                errors.append(e)
            except AttributeError as e:
                value = f(value, datagraph)
        if errors: 
            raise ValidationErrorStack(errors)


class ArrayContext(VinoContext):

    def validate(self, data):
        for runner in self.stack:
            runner.run(data)

    def run(self, value):
        # ensures that value is None or if not set 
        # otherwise ensures that value is set to a non-dict sequence 
        # then attempts to convert it to a list
        pass


class ArrayItemsContext(VinoContext):

    qualifiers = []

    def validate(self, data):
        rv = []
        for i, d in enumerate(data):
            # no qualifiers implies all items qualify
            if (not self.qualifiers) or self.itemself._qualify(i,d):
                rv.append(self._run_stack(d))
        return rv

    def _run_stack(self, data):
        for runner in self.stack:
            data = runner.run(data)
        return data

    def _qualify(self, index, data):
        for q in self.item_qualifiers:
            if q(index, data):
                return True
        return False

    def apply_to(qualifier):
        self.qualifiers.append(qualifier)
        return self


class ObjectContext(VinoContext): pass

class ObjectPropertyContext(VinoContext): pass
 
class StreamContext(VinoContext): pass
