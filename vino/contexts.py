from .errors import VinoError, ValidationError, ValidationErrorStack
from .processors.runners import RunnerStack
from . import utils
from .processors import processors as proc
from .qualifiers import ItemQualifierStack, MemberQualifierStack

class Context:
    ''' The Context represent the primary scope of influence of a processor.
    Basic JSON elements (number, string, boolean, null) have a single context,
    within which the processors declared can influence the data. Array and
    Object elements each can have one or more scopes. The primary scope is for
    the constructs themselves, while their items or properties are handled in
    sub-scopes.
    '''
    def __init__(self, *processors):
        """ The initializer doesn't do anything other than providing some
        convenience for adding processors at declaration time.
        """
        # prepend context to list of processors
        #processors = (self,) + processors
        self.add(*processors)

    def add(self, *processors):
        """ add processors """
        def _tuplefy(p):
            try: 
                return tuple(p):
            except TypeError as e:
                return (p, None)
        processors = (_tuplefy(p) for p in processors)
        self.runners.add(*processors)

    @property
    def runners(self):
        if not hasattr(self, '_runners'):
            self._runners = RunnerStack(self)
        return self._runners

    def validate(self, data):
        """ This method is typically called as an entry point for a root
        Context object. When a Context is a subset part of another Context, its
        `run()` method is called instead by a Runner, receiving all necessary
        data and metadata to apply its processes on the relevant part of it.
        """
        return self.run(data, self)

    def run(self, data, context):
        """ Let's quack like a Processor """
        # default behaviour is to simply return a copy of the data
        return self.runners.run(data)

    def apply_to(self):
        raise NotImplementedError(
            '`Context.apply_to` is a specialty property that should be '
            'implemented in a subclass of `Context`.')

    #def run(self, data, context):
    #    if data is None:
    #        return None
    #    rv = []
    #    for i, v in enumerate(data):
    #        # no qualifiers implies all items qualify
    #        if self.qualifier and (self.qualifiers.empty() 
    #                               or self.qualifiers.qualify(i,v)):
    #            rv.append(self._runners.run(v))
    #        else:
    #            rv.append(v)
    #    return rv

    #def indexes(self, *qualifiers):
    #    if not self.member_qualifiers.empty()::
    #        raise err.VinoError(
    #            'Attempt at using a Context as Array bound, '
    #            'that was previously declared as Object bound. '
    #            'Context cannot belong to both Object and Array '
    #            'at the same time.')
    #    self.item_qualifiers.add(*qualifiers)
    #    return self

    #def attributes(self, *qualifiers):
    #    if not self.item_qualifiers.empty()::
    #        raise err.VinoError(
    #            'Attempt at using a Context as Object bound, '
    #            'that was previously declared as Array bound. '
    #            'Context cannot belong to both Object and Array '
    #            'at the same time.')
    #    self.member_qualifiers.add(*qualifiers)
    #    return self

    # aliasing
    indices = indexes
    members = properties = attributes

class BasicContext(Context):

    def __init__(self, *processors): 
        basic_type_proc = (proc.is_basic_type, False) # no qualifiers allowed
        processors = (basic_type_proc,) + processors
        super(BasicContext, self).__init__(*processors)


class ArrayContext(Context):
    def __init__(self, *processors, **kw): 
        array_type_proc = (proc.is_array_type, False) # no qualifiers allowed
        processors = (array_type_proc,) + processors
        super(ArrayContext, self).__init__(*processors, **kw)

    def run(self, data, context):
        return self.runners.run(data)
    
    @property
    def qualifiers(self):
        if not hasattr(self, '_qualifiers'):
            self._qualifiers = ItemQualifierStack(self)
        return self._qualifiers

    def apply_to(self, *qualifiers):
        qualifier_stack = ItemQualifierStack()
        self.runners.add_qualifiers(qualifier_stack, *qualifiers)
        return self


class ArrayItemsContext(Context):

    @property
    def qualifiers(self):
        if hasattr(self, '_qualifiers'):
            return self._qualifiers
        self._qualifiers = ItemQualifierStack(self)
        return self._qualifiers

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

class ObjectContext(Context):
    def __init__(self, *processors, **kw): 
        object_type_proc = (proc.is_object_type, False) # no qualifiers allowed
        processors = (object_type_proc,) + processors
        super(ObjectContext, self).__init__(*processors, **kw)

    def apply_to(self, *qualifiers):
        qualifier_stack = MemberQualifierStack()
        self.runners.add_qualifiers(qualifier_stack, *qualifiers)
        return self

class ObjectMembersContext(Context):

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
