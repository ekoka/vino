from .errors import VinoError, ValidationError, ValidationErrorStack
from .processors.runners import RunnerStack
from . import utils

class VinoContext:
    ''' The Context represent the primary scope of influence of a processor.
    Basic JSON elements (number, string, boolean, null) have a single context,
    within which the processors declared can influence the data. Array and
    Object elements each have two scopes, one for the constructs themselves
    and one for their items or properties.
    '''
    def __init__(self, *processors, **kw): 
        self.name = kw.pop('name', None) # name is a keyword-only argument
        # prepend context to list of processors
        processors = (self,) + processors
        self._runners = RunnerStack(self, *processors)

    def run(self, value, context):
        """ Let's quack like a Processor """
        # default behaviour is to simply return the value untouched
        return value


class BasicContext(VinoContext):
        
    def validate(self, value):
        # raises ValidationErrorStack
        value = self._runners.run(value)
        return value

    def run(self, value, context):
        if (utils.is_str(value) or utils.is_numberlike(value) 
            or utils.is_boolean(value) or value is None):
            return value
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Array type.', type(value))


        # TODO: handle bytes somehow
        # if utils.is_iterable(value, exclude_dict=False):
        #     raise errors.ValidationError('Expected Basic Type ')



class ArrayContext(VinoContext):

    def validate(self, value):
        value = self._runners.run(value)
        return value

    def run(self, value, context):
        # ensures that value is None or if not set 
        # otherwise ensures that value is set to a non-dict sequence 
        # then attempts to convert it to a list
        if value is None:
            return None
        if utils.is_iterable(value, exclude_set=True):
            return list(value)
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Array type.', 
            type(value))



class ArrayItemsContext(VinoContext):

    qualifiers = []

    def run(self, value):
        for i, v in enumerate(value):
            # no qualifiers implies all items qualify
            if (not self.qualifiers) or self._qualify(i,v):
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

    def apply_to(*qualifiers):
        for q in qualifiers:
            self.qualifiers.append(self._qualifier(q))
        return self

    def _qualifier(qualifier):
        if utils.is_integer(q):
            return [q]
        if utils.is_iterable(q):
            return list(q)
        if callable(q):
            return q



class ObjectContext(VinoContext): pass

class ObjectPropertyContext(VinoContext): pass
 
class StreamContext(VinoContext): pass
