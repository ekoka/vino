from .processors.runners import RunnerStack

class Context:
    ''' The Context represent the primary scope of influence of a processor.
    Basic JSON elements (number, string, boolean, null) have a single context,
    within which the processors declared can influence the data. Array and
    Object elements each can have one or more scopes. The primary scope is for
    the constructs themselves, while their items or properties are handled in
    sub-scopes.
    '''

    _default_runner_stack_cls = RunnerStack

    def __init__(self, *processors, **kwargs):
        self.runner_stack_cls = kwargs.pop(
            'runner_stack_cls', Context._default_runner_stack_cls)
        self.qualifier_stack_cls = kwargs.pop('qualifier_stack_cls', None)

        """ The initializer doesn't do anything other than providing some
        convenience for adding processors at declaration time.
        """
        self.expand(*processors)

    def _tuplefy(self, processor):
        try: 
            return processor[:1] + processor[1:]
        except (TypeError, IndexError) as e:
            return (processor, None)

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

    def spawn(self):
        constructor =  self.__class__
        rv = constructor()
        rv.runners = self.runners.copy(rv)
        return rv

    def apply_to(self, *qualifiers):
        tpl = (self,) + qualifiers
        return self._tuplefy(tpl)

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

class StreamContext: pass
class UnspecifiedContext: pass
