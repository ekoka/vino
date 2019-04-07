from collections import namedtuple
from .. utils import _undef
from .. import errors as err

class Runner:

    ProcProxy = namedtuple('ProcProxy', 
                        'run default override failsafe raw_processor')

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
        self._raw_processor = processor
        self.name = getattr(processor, 'name', None)
        self.processor = self.get_processor_proxy(processor)

    @classmethod
    def get_processor_proxy(cls, processor):
        default = getattr(processor, 'default', None)
        override = getattr(processor, 'override', None)
        failsafe = getattr(processor, 'failsafe', None)
        run = getattr(processor, 'run', None)
        if run is None: 
            if callable(processor):
                run = processor
            else:
                name = getattr(processor, 'name', None) or repr(processor)
                raise err.VinoError('Invalid Processor {}'.format(name))
        return cls.ProcProxy(run, default, override, failsafe, processor)

    def run_override(self, override=None, data=_undef, state=None):
        if override:
            for fnc in override:
                data = fnc(data=data, state=state)
        return data

    def run_default(self, default=None, data=_undef, state=None):
        if default:
            for fnc in default:
                data = fnc(data=data, state=state)
        return data

    def run_failsafe(self, failsafe, data=_undef, state=None):
        if failsafe:
            for fnc in failsafe:
                data = fnc(data=data, state=state)
            return data
        raise err.ValidationError('failsafe')

    def save_or_fail(
        self, failsafe, error, data=_undef, state=None, message=None):
        try:
            rv = self.run_failsafe(failsafe, data=data, state=state)
        except err.ValidationError as e:
            raise error
        return rv

    def run(self, data=_undef, state=None):
        processor = self.processor

        # override
        if processor.override:
            data = self.run_override(override=processor.override, data=data,
                                     state=state)

        # default when data is missing
        if data is _undef and processor.default:
            data = self.run_default(processor.default, data=data, state=state)

        try:
            # run
            data = processor.run(data, state)
        except err.ValidationError as error:
            # save or fail
            data = self.save_or_fail(failsafe=processor.failsafe, error=error,
                                     data=data, state=state)
        return data


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
        # processors should be a list of tuples with each item having the 
        # either of these structures:
        # (processor, q1, q2, q3)
        # (processor, None)
        # (processor, False)
        for processor in processors:
            try:
                processor, qualifiers = processor[0], processor[1:]
            except TypeError:
                raise err.VinoError(
                    'Each processor and its qualifiers must be specified in '
                    'tuples.')
            runner = Runner(processor)
            if len(qualifiers)==1 and qualifiers[0] is False:
                # this situation arises when the processor does not take a 
                # qualifier.
                self.runners.append({'runner': runner, 'qualifiers': False})
            else:
                #TODO: clean this up. If the runner has qualifiers then 
                # make the runner an object, rather than a dict.
                self.runners.append({'runner': runner, 'qualifiers': None})
                if len(qualifiers)>1 or qualifiers[0] is not None:
                    self.add_qualifiers(*qualifiers)

    def add_qualifiers(self, *qualifiers):
        if not self.runners:
            # emtpy stack
            raise err.VinoError(
                'Cannot add qualifier without specifying a processor')
        # let' grab the runner we just appended from `self.add()`
        runner = self.runners[-1]
        if runner['qualifiers'] is False:
            raise err.VinoError('The processor does not accept qualifiers')
        if runner['qualifiers'] is None:
            if self.context is None: 
                raise err.VinoError(
                    'RunnerStack must be given a Context object to enable '
                    'implicit creation of QualifierStack objects.')
            if self.context.qualifier_stack_cls is None:
                raise err.VinoError(
                    'A QualifierStack constructor must be specified for this '
                    'Context to enable implicit creation of QualifierStack '
                    'objects.')
            # create qualifier stack for this runner stack
            runner['qualifiers'] = self.context.qualifier_stack_cls()
        # merge with previous qualifiers
        runner['qualifiers'].add(*qualifiers)

    def run(self, data, **kw):
        e_stack = err.ValidationErrorStack('Validation Errors')
        #if self.context:
        state = self.context.make_state() if self.context else None
        #state = {'matches':self.context.init_matches(), 'context': self.context}
        for runner in self.runners:
            r,q = runner['runner'],runner['qualifiers']
            try:
                if q: 
                    data = q.apply(data, r, state)
                else:
                    data = r.run(data, state)
                # if data set or left to undef interrupt processing for it
                if data is _undef:
                    break
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


