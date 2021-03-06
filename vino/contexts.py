from . import utils as uls 
from .processors.runners import RunnerStack
from . import errors 

class Context:
    ''' The `Context` represent the scope of influence of the processors in a
    validation declaration. `Contexts` for primitive JSON elements (number,
    string, boolean, null) have a simple scope, within which the declared
    processors can influence the declared element.

        >>> from vino.contexts import Context 
        >>> from vino import isnot_int, allowempty, allownull, required
        >>> name = Context(
        ...    isnot_int, 
        ...    allownull,
        ...    allowempty,
        ...    ~required,
        ... )
        >>> name.validate('Michael')
        Michael
    
    By contrast, Array and Object schemas would require multiple scopes. The
    main scope would handle the container element itself (the object or the
    array), while their contained items or properties would be handled in their
    own sub-Contexts.

        user = Context(
            
            
        )
    '''

    _default_runner_stack_cls = RunnerStack

    def __init__(self, *processors, **kwargs):
        self.runner_stack_cls = kwargs.pop(
            'runner_stack_cls', Context._default_runner_stack_cls)
        self.qualifier_stack_cls = kwargs.pop('qualifier_stack_cls', None)
        self.expand(*processors)

    def _tuplefy(self, processor):
        # ensures that processor is returned in tuple form, with actual
        # processor on the left and qualifiers, if any, on the right.
        try: 
            # return (processor, ) + (qualifier1, qualifier2, ...)
            return processor[:1] + processor[1:]
        except (TypeError, IndexError) as e:
            # or return (processor, None)
            return (processor, None)

    def spawn(self):
        cls =  self.__class__
        rv = cls.__new__(cls)
        rv.runner_stack_cls=self.runner_stack_cls
        rv.qualifier_stack_cls=self.qualifier_stack_cls
        rv.runners = self.runners.copy(rv)
        return rv

    @property
    def runners(self):
        if not hasattr(self, '_runners'):
            self._runners = self.runner_stack_cls(self)
        return self._runners

    @runners.setter
    def runners(self, _runners):
        self._runners = _runners

    def expand(self, *processors):
        processors = (self._tuplefy(p) for p in processors)
        self.runners.add(*processors)

    def add(self, *processors):
        """ To make Context more immutable this method does not extend its
        own Context, but rather spawns a new one to which it gives the same 
        processors that it previously registered.
        """
        rv = self.spawn()
        rv.expand(*processors)
        return rv

    def apply_to(self, *qualifiers):
        tpl = (self,) + qualifiers
        # tpl is already in tuple form, but still call _tuplefy in case further
        # logic is added to it in the future.
        return self._tuplefy(tpl)

    def validate(self, data=uls._undef):
        """ This method is typically called as an entry point for a root
        Context object. When a Context is a subset part of another Context, its
        `run()` method is called instead by a Runner, receiving all necessary
        data and metadata to apply its processes on the relevant part of the 
        data.
        """
        return self.run(data, self)

    def run(self, data, context):
        """ Let's quack like a Processor, i.e. Context treated as Processor """
        # default behaviour is to simply return a copy of the data
        return self.runners.run(data)

    def make_state(self):
        return {
            'matches': self.init_matches(),
            'context': self,
        }

    def init_matches(self): 
        # TODO: This seems a bit circuitous. Should the Context really be the
        # one to initiate matches?
        if self.qualifier_stack_cls:
            return self.qualifier_stack_cls.init_matches()

class StreamContext: pass
class UnspecifiedContext: pass
