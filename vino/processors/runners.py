from .. utils import _undef
from .. import errors as err

class Runner:
    def __init__(self, processor):
        """ Provides a simple interface to run a process. 
        
        The Runner allows to decouple the Processor's initialization steps from
        the Context. By being wrapped in a third-party object, it simplifies
        the interface the Context needs to work with.

        If a processor has a `vino_init()` method it will be called.
        It allows to pass a construct to vino that may have to return some
        other object as processor. This is how the native `BooleanProcessors`
        work when not instantiated. For example When specifying adding a
        `vino.mandatory` processor its construction is simply delayed and a
        call to its `vino_init()` method is made here, which returns an actual
        instance for the Runner to work with.
        """
        try: 
            # calling an initializer if any
            processor = processor.vino_init()
        except AttributeError:
            pass
        self.name = getattr(processor, 'name', None)
        self.processor = self._valid_processor(processor)

    def _valid_processor(self, processor):
        if hasattr(processor, 'run'):
            return lambda *a, **kw: processor.run(*a, **kw)
        if callable(processor):
            return processor
        name = self.name or repr(processor)
        raise err.VinoError('Invalid Processor {}'.format(name))

    def run(self, data, context=None):
        return self.processor(data, context)


class RunnerStack:
    """ A stack of Runners.
    
    TODO: some processors should be excluded from some contexts.
    """
    def __init__(self, context, *processors):
        self.context = context
        # the stack consists in a list of
        # {'runner':Runner, 'qualifiers': qualifiers) objects
        self.add(*processors)

    @property
    def runners(self):
        if not hasattr(self, '_runners'):
            self._runners = []
        return self._runners

    @runners.setter
    def runners(self, _runners):
        self._runners = _runners

    def add(self, *processors):
        for processor in processors:
            try:
                processor, qualifiers = processor[0], processor[1:]
            except TypeError:
                raise err.VinoError(
                    'Each processor and its qualifiers must be specified in '
                    'tuples.')
            runner = Runner(processor)
            if len(qualifiers)==1 and qualifiers[0] is False:
                self.runners.append({'runner': runner, 'qualifiers': False})
            else:
                self.runners.append({'runner': runner, 'qualifiers': None})
                if len(qualifiers)>1 or qualifiers[0] is not None:
                    self.add_qualifiers(*qualifiers)

    def add_qualifiers(self, *qualifiers):
        if not self.runners:
            # emtpy stack
            raise err.VinoError(
                'Cannot add qualifier without specifying a processor')
        runner = self.runners[-1]
        if runner['qualifiers'] is False:
            raise err.VinoError('The processor does not accept qualifiers')
        if runner['qualifiers'] is None:
            if self.context is None: 
                raise err.VinoError(
                    'RunnerStack must be given a Context object to enable '
                    'implicit creation of QualifierStack objects.')
            if self.context._qualifier_stack_constructor is None:
                raise err.VinoError(
                    'A QualifierStack constructor must be specified for this '
                    'Context to enable implicit creation of QualifierStack '
                    'objects.')
            runner['qualifiers'] = self.context._qualifier_stack_constructor()
        # merge with previous qualifiers
        runner['qualifiers'].add(*qualifiers)

    def run(self, data, **kw):
        e_stack = err.ValidationErrorStack('Validation Errors')
        for runner in self.runners:
            r,q = runner['runner'],runner['qualifiers']
            try:
                if q: 
                    data = q.apply(data, r, self.context)
                else:
                    data = r.run(data, self.context)
            except err.ValidationError as e:
                self._copy_data_in_err(e, data)
                e_stack.append(e)
                if e.interrupt_validation:
                    break
        if e_stack.empty:
            return data
        self._copy_data_in_err(e_stack, data)
        raise e_stack

    def copy(self, context=None):
        """ This spawns and returns a new RunnerStack loaded up with currently
        registered Runners.
        """
        if context is None:
            context = self.context
        if context is False:
            context = None

        constructor = self.__class__
        rv = constructor(context)
        rv.runners = self.runners[:]
        return rv

    def _copy_data_in_err(self, e, data):
        # try to make shallow copy
        try:
            e.data = data.copy()
        except AttributeError:
            e.data = data

    def __len__(self):
        return len(self.runners)

    def __getitem__(self, index):
        return self.runners[index]


