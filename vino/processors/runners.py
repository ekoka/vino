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


# NOTE: I'm not sure this is still needed
#class ContextRunner(Runner):
#    def __init__(self, context):
#        self.context = self._valid_context(context)
#
#    def _valid_context(self, context):
#        if hasattr(context, 'validate'):
#            return context
#
#    def run(value, context=None):
#        self.context.validate(value, context)

class RunnerStack:
    """ A stack of Runners.
    
    TODO: some processors should be excluded from some contexts.
    """
    def __init__(self, context, *processors):
        self.context = context
        self.runners = []
        for i, p in enumerate(processors):
            try:
                runner = ProcessorRunner(p)
                # TODO: change the isinstance to make the API more flexible
                # and duck-typable.
                from ..contexts import ObjectContext
                if runner.name and not isinstance(context, ObjectContext):
                    raise err.VinoError('The context enclosing {} does not '
                                        'appear to be an Object context, yet '
                                        '{} is declared with a name.'.format(
                                        p, p))
                

            except err.VinoError:
                raise
                # NOTE: this will not be called for Contexts since they now 
                # mimick Processor's API

                # is this an ArrayItemsContext-like object?
                runner = ContextRunner(p)
                # check that the object has 
            self.runners.append(runner)

    def run(self, data):
        e_stack = err.ValidationErrorStack('Validation Errors')
        for r in self.runners:
            try:
                if r.name:
                    """ If it has a name it's implied that its parent context
                    is an Object and that the data should be subscriptable.
                    """
                    try:
                        # changing context
                        value = data.get(r.name, _undef)
                        data[r.name] = r.run(value, self.context)
                    except AttributeError as e:
                        """ The attribute was not found on the data """
                        raise err.ValidationError(
                            'Could not find  "{}": {}'
                                .format(r.name, ))
                    except TypeError as e:
                        """ We're working from the wrong data type. How did
                        we get here?"""
                        raise err.ValidationError(
                            ' "{}": {}'
                                .format(r.name, ))
                else:
                    value = data
                    data = r.run(value, self.context)
            except err.ValidationError as e:
                self._copy_data_in_err(e, data)
                e_stack.append(e)
                if e.interrupt_validation:
                    break
        if e_stack.empty:
            return data
        self._copy_data_in_err(e_stack, data)
        raise e_stack

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


