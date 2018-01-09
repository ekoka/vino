from .errors import VinoError, ValidationError, ValidationErrorStack
from .processors.runners import RunnerStack
from . import utils
from .processors.processors import Processor
from .qualifiers import ItemQualifierStack

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
        #processors = (self,) + processors
        self._runners = RunnerStack(self, *processors)

    def validate(self, value):
        # if we're calling validate to this object then it's the root
        # object and it needs to run itself
        # TODO: maybe give it a runner to be consistent
        # temporarily adding this object to its runner
        value = self._runners.run(value)
        return value

    def run(self, value, context):
        """ Let's quack like a Processor """
        # default behaviour is to simply return the value untouched
        return value

class BasicTypeProcessor(Processor):
    def run(self, value, context):
        if (utils.is_str(value) or utils.is_numberlike(value) 
            or utils.is_boolean(value) or value is None):
            return value
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Array type.', type(value))


class BasicContext(VinoContext):

    def __init__(self, *processors, **kw): 
        processors = (BasicTypeProcessor(),) + processors
        super(BasicContext, self).__init__(*processors, **kw)

    def run(self, value, context):
        return self._runners.run(value) 
        # TODO: handle bytes somehow
        # if utils.is_iterable(value, exclude_dict=False):
        #     raise errors.ValidationError('Expected Basic Type ')



class ArrayTypeProcessor(Processor):
    def run(self, value, context):
        # ensures that value is None or if not set 
        # otherwise ensures that value is set to a non-dict sequence 
        # then attempts to convert it to a list
        if value is None:
            return None
        if utils.is_iterable(value, exclude_set=True, 
                             exclude_generator=True):
            return list(value)
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Array type.', 
            type(value))

class ArrayContext(VinoContext):
    def __init__(self, *processors, **kw): 
        processors = (ArrayTypeProcessor(),) + processors
        super(ArrayContext, self).__init__(*processors, **kw)

    def run(self, value, context):
        return self._runners.run(value)

class ArrayItemsContext(VinoContext):

    @property
    def qualifiers(self):
        if hasattr(self, '_qualifiers'):
            return self._qualifiers
        self._qualifiers = ItemQualifierStack(self)
        return self._qualifiers

    def validate(self, value):
        return self.run(value, self)

    def run(self, value, context):
        if value is None:
            return None
        rv = []
        for i, v in enumerate(value):
            # no qualifiers implies all items qualify
            if self.qualifiers.empty() or self.qualifiers.qualify(i,v):
                rv.append(self._runners.run(v))
            else:
                rv.append(v)
        return rv

    def apply_to(self, *qualifiers):
        self.qualifiers.add(*qualifiers)
        return self

class ObjectTypeProcessor(Processor):
    def run(self, value, context):
        # ensures that value is None or if not set 
        # otherwise ensures that value is set to a non-dict sequence 
        # then attempts to convert it to a list
        if value is None:
            return None
        try:
            if utils.is_dict(value):
                return dict(value)
        except:
            pass
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Object type.', 
            type(value))


class ObjectContext(VinoContext):
    def __init__(self, *processors, **kw): 
        processors = (ObjectTypeProcessor(),) + processors
        super(ObjectContext, self).__init__(*processors, **kw)

class ObjectPropertyContext(VinoContext): pass
 
class StreamContext(VinoContext): pass
