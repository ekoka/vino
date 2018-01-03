class Runner:
    def run(self, *a, **kw):
        raise NotImplementedError()

class ProcessorRunner(Runner):
    def __init__(self, processor):
        """ Provides a simple interface to run a process. 
        
        The Runner allows to decouple the Processor's initialization steps from
        the Context. By being wrapped in a third-party object, it simplifies
        the interface the Context needs to work with.

        If a processor has a `vino_init()` method it will be called.
        It allows to pass a construct to vino that may have to return some
        other object as processor. This is how the native `BooleanProcessor`
        work when not instantiated. When working with a `vino.mandatory`
        processor its construction is simply delayed and a call to `init is
        made here.
        """
        if hasattr(processor, 'vino_init'): 
            # calling an initializer if any
            processor = processor.vino_init()
        self.processor = self._valid_processor(processor)

    def _valid_processor(self, processor):
        if hasattr(processor, 'run'):
            return lambda *a, **kw: processor.run(*a, **kw)
        if callable(processor):
            return processor
        name = (processor.name 
                if hasattr(processor, 'name') 
                else repr(processor))
        raise VinoError('Invalid Processor {}'.format(name))

    def run(value, context=None):
        self.processor.run(value, context)

class ContextRunner(Runner):
    def __init__(self, context):
        self.context = self._valid_context(context)

    def _valid_context(self, context):
        if hasattr(context, 'validate'):
            return context

    def run(value, context=None):
        self.context.validate(value, context)

class RunnerStack:
    """ A stack of Runners.
    
    TODO: some processors should be excluded from some contexts.
    """
    def __init__(self, context, *processors):
        self.context = context
        for p in processors:
            try:
                runner = ProcessorRunner(p)
            except VinoError:
                # is this an ArrayItemsContext-like object?
                runner = ContextRunner(p)
                # check that the object has 
            self.runners.append(runner)

    def run(self, value):
        for r in self.runners:
            value = r.run(value, self.context)

class Qualifier:
    def qualify(self, item, index=None): pass


class SequenceQualifier(Qualifier):

    def __init__(self, start=0, step=None, stop=None):
        """ specifies a range of items to qualify """
        self. items = self.set_sequence(start, step, stop)

    def set_sequence(self, start, step, stop):
        if is_rangelike(start):
            if not (stop is None is step):
                raise VinoError(
                    'Cannot mix range object with additional arguments in '
                    'sequence call.')
            start, stop, step = start.start, start.stop, start.step
        elif is_listlike(start): # we don't want no generators!
            rv = self._list_to_range(start, step)
            
        for n,s in dict(start=start, stop=stop, step=step):
            try:
                s = abs(s)-1 if n=='step' else s
                if not is_intlike(s, positive=True):
                    raise TypeError()
            except TypeError:
                raise VinoError(
                    'Invalid {} value given for sequence: {}'.format(n,s))

        return range(start, stop, step)

    def __invert__(self):
        """ switch between qualifier and disqualifier """
        _current = self._qualifier_fnc
        self._qualifier_fnc = {
            self._qualify: self._disqualify,
            self._disqualify:self._qualify}[_current]
        return self

    def _qualify(self, *a, **kw):
        pass

    _qualifier_fnc = _qualify

    def _disqualify(self, *a, **kw):
        pass

seq = sequence = SequenceQualifier
