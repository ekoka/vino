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

    def validate(self, data):
        # if we're calling validate to this object then it's the root
        # object and it needs to run itself
        # TODO: maybe give it a runner to be consistent
        # temporarily adding this object to its runner
        data = self._runners.run(data)
        return data

    def run(self, data, context):
        """ Let's quack like a Processor """
        # default behaviour is to simply return the data untouched
        return data

class BasicTypeProcessor(Processor):
    def run(self, data, context):
        if (utils.is_str(data) or utils.is_numberlike(data) 
            or utils.is_boolean(data) or data is None):
            return data
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Array type.', type(data))


class BasicContext(VinoContext):

    def __init__(self, *processors, **kw): 
        processors = (BasicTypeProcessor(),) + processors
        super(BasicContext, self).__init__(*processors, **kw)

    def run(self, data, context):
        return self._runners.run(data) 
        # TODO: handle bytes somehow
        # if utils.is_iterable(data, exclude_dict=False):
        #     raise errors.ValidationError('Expected Basic Type ')



class ArrayTypeProcessor(Processor):
    def run(self, data, context):
        # ensures that data is None or if not set 
        # otherwise ensures that data is set to a non-dict sequence 
        # then attempts to convert it to a list
        if data is None:
            return None
        if utils.is_iterable(data, exclude_set=True, 
                             exclude_generator=True):
            return list(data)
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Array type.', 
            type(data))

class ArrayContext(VinoContext):
    def __init__(self, *processors, **kw): 
        processors = (ArrayTypeProcessor(),) + processors
        super(ArrayContext, self).__init__(*processors, **kw)

    def run(self, data, context):
        return self._runners.run(data)

class ArrayItemsContext(VinoContext):

    @property
    def qualifiers(self):
        if hasattr(self, '_qualifiers'):
            return self._qualifiers
        self._qualifiers = ItemQualifierStack(self)
        return self._qualifiers

    def validate(self, data):
        return self.run(data, self)

    def run(self, data, context):
        if data is None:
            return None
        rv = []
        for i, v in enumerate(data):
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
    def run(self, data, context):
        # ensures that data is None or if not set 
        # otherwise ensures that data is set to a non-dict sequence 
        # then attempts to convert it to a list
        if data is None:
            return None
        try:
            if utils.is_dict(data):
                return dict(data)
        except:
            pass
        # TODO more descriptive message
        raise ValidationError(
            'Wrong type provided. Expected Object type.', 
            type(data))


class ObjectContext(VinoContext):
    def __init__(self, *processors, **kw): 
        processors = (ObjectTypeProcessor(),) + processors
        super(ObjectContext, self).__init__(*processors, **kw)

class ObjectMembersContext(VinoContext):
    def validate(self, data):
        return self.run(data, self)

    def run(self, data, context):
        """
        - if runners map to members iterate through them first and validate each
        - elif qualifiers are set, iterate through them if list of keys and apply
        runners to each.
        - if 
        """
        if data is None:
            return None

        for r in self._runners:
            if self.qualifiers.empty() or self.qualifiers.qualify():
                pass
        rv = {}
        for k, v in data.items():
            # no qualifiers implies all items qualify
            if self.qualifiers.empty() or self.qualifiers.qualify(k,v):
                rv[k] = self._runners.run(v)
            else:
                rv[k] = v
        return rv

    #def run(self, data, context):
    #    if data is None:
    #        return None
    #    rv = {}
    #    for k, v in data.items():
    #        # no qualifiers implies all items qualify
    #        if self.qualifiers.empty() or self.qualifiers.qualify(k,v):
    #            rv[k] = self._runners.run(v)
    #        else:
    #            rv[k] = v
    #    return rv

class StreamContext: pass
class UnspecifiedContext: pass
