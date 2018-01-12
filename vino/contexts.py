from .processors.runners import RunnerStack

class Context:
    ''' The Context represent the primary scope of influence of a processor.
    Basic JSON elements (number, string, boolean, null) have a single context,
    within which the processors declared can influence the data. Array and
    Object elements each can have one or more scopes. The primary scope is for
    the constructs themselves, while their items or properties are handled in
    sub-scopes.
    '''

    _qualifier_stack_constructor = None

    def __init__(self, *processors):
        """ The initializer doesn't do anything other than providing some
        convenience for adding processors at declaration time.
        """
        self.add(*processors)

    def _tuplefy(self, processor):
        try: 
            return processor[:1] + processor[1:]
        except (TypeError, IndexError) as e:
            return (processor, None)

    def add(self, *processors):
        """ add processors """
        processors = (self._tuplefy(p) for p in processors)
        self.runners.add(*processors)

    def apply_to(self, *qualifiers):
        tpl = (self,) + qualifiers
        return self._tuplefy(tpl)

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

class StreamContext: pass
class UnspecifiedContext: pass
