from . import errors
""" This file describes the schema mappings of JSON's basic types """

class ProcessorRunner:
    def __init__(self, processor):
        if hasattr(processor, 'vino_init'): 
            # calling a constructor if any
            processor = processor.vino_init()
        processor = self._valid_processor(processor)
        self.processor = processor

    def _valid_processor(self, processor):
        if hasattr(processor, 'run'):
            return lambda *a, **kw: processor.run(*a, **kw)
        if callable(processor):
            return processor
        name = (processor.name 
                if hasattr(processor, 'name') 
                else repr(processor))
        raise errors.VinoError('Invalid Processor {}'.format(name))

    def run(value, schema):
        self.processor.run(value, schema)

class RunnerBatch:
    def __init__(self, schema, *processors):
        self.schema = schema
        for p in processors:
            self.runners.append(ProcessorRunner(p))

    def run(self, value):
        for r in self.runners:
            value = r.run(value, self.schema)

class ArrayRunnerBatch:
    def __init__(self, schema, *processors):
        self.schema = schema
        for p in processors:
            if isinstance(p, ArrayItemsContext): # for list of items
                pass
            self.runners.append(ProcessorRunner(p))
#def VinoGraph: pass
#
#def ObjectGraph(VinoGraph): pass
#
#def ArrayGraph(VinoGraph):
#    def __init__(self, schema):

class VinoContext:
    ''' The Context represent the primary scope of influence of a processor.
    Basic JSON elements (number, string, boolean, null) have a singel scope,
    within which the processors declared can influence the data. Array and
    Property elements each have two scopes, one for the constructs themselves
    and one their items or properties.
    '''
    def __init__(self, name=None, *processors):
        if name is None:
            raise errors.VinoError('None type is not a valid processor.')
        if isinstance(name, str):
            self.name = name
        else:
            self.name = None
            processors = [name]+processors
        self.make_batch(*processors)

    def qualify(self, qualifier, *a, **kw):
        """ just a generic adapter using the visitor pattern """
        qualifier.qualify(self, *a, **kw)
        


class ObjectContext(VinoContext): pass
class ObjectPropertyContext(VinoContext): pass

class BasicContext(VinoContext):

    def make_batch(*processors):
        self.batch = RunnerBatch(self, *processors)
        
    def validate(self, value):
        errors = []
        result = None
        for f in self.processors:
            try:
                value = f.run(value)
            else errors.ValidationError as e:
                if e.interrupt_validation: #  
                    raise e
                errors.append(e)
            else AttributeError as e:
                value = f(value, datagraph)
        if errors: 
            raise errors.ErrorCollection(errors)

PER_ITEM = 0
PER_PROCESSOR = 1

class ArrayContext(VinoContext, Qualifier):
    def make_batch(self, *processors):
        for p in processors:
            if p 

    def validate(self, data, ordering_scheme=PER_ITEM):
        pass

    def qualify(self, item, index):
        pass

class ArrayItemsContext(VinoContext):
    def make_batch(*processors):
        for p in processors:
            if isinstance(p, ProcessorBundle):

class Qualifier:
    def qualify(self, item, index=None):
        if item

def is_rangelike(r):
    return (False if (not hasattr(r, 'start')) 
            or (not hasattr(r, 'stop'))
            or (not hasattr(r, 'step')) 
            else True)

def is_listlike(l):
    try:
        len(l)
        return True
    except:
        return False

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
            return self._list_to_range(start, step)
            
        for n,s in dict(start=start, stop=stop, step=step):
            try:
                s = abs(s)-1 if n=='step' else s
                if s < 0 or not isinstance(s, int):
                    raise TypeError()
            except TypeError:
                raise VinoError(
                    'Invalid {} value given for sequence: {}'.format(n,s))

        self.items = self._list_to_range(start, stop, step)

    def __invert__(self):
        """ turn the Qualifier into a disqualifier """
        self._qualifier_fnc = {
            self._qualify: self._disqualify, self._disqualify:self._qualify}[
                self._qualifier_fnc]
        return self

    def _qualify(self):
        pass

    _qualifier_fnc = _qualify

    def _disqualify(self):
        pass

seq = sequence = SequenceQualifier


class ProcessorBundle:
    """ This class packs a sequence of processors to apply to a group
    of items. """
    def __init__(self, *processors):
    
    def apply_to(*qualifiers):
        """a qualifier can be many things:
            - a range in the form of a range object or a list: in which case
            the listed validation steps will apply to all items whose index
            falls within the list returned by the range. 
            - a function: which should return True for an item before the 
            validation steps proceed.
        """
        self.qualifiers = qualifiers


some = ProcessorBundle
every = lambda *a: return ProcessorBundle(0, *processors)
