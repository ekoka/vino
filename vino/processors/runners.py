from .. utils import _undef
from .. import errors as err

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
        self.runners = []
        self.add(*processors)

    def add(self, *processors):
        for p, qualifiers in processors:
            runner = ProcessorRunner(p)
            # TODO: change the isinstance to make the API more flexible
            # and duck-typable.
            from ..contexts import ObjectContext
            # TODO: move this. The name will be in the QualifierStack not
            # the Runner.
            if runner.name and not isinstance(context, ObjectContext):
                raise err.VinoError(
                    'The context enclosing {} does not appear to be an Object '
                    'context, yet {} is declared with a name.'.format(p, p))
            self.runners.append({'runner': runner, 'qualifiers': qualifiers})

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

    def add_qualifiers(self, qs, *qualifiers):
        if not self.runners:
            # emtpy stack
            raise err.VinoError(
                'Cannot add qualifier without specifying a processor')
        runner = self.runners[-1]
        if runner['qualifiers'] is False:
            raise err.VinoError('The processor does not accept qualifiers')
        if runner['qualifiers'] is None:
            runner['qualifiers'] = qs
        # merge with previous qualifiers
        runner['qualifiers'].add(*qualifiers)


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


