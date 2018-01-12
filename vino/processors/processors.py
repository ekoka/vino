from ..utils import _undef
from .. import errors as err
from .. import utils
import functools

class Processor: pass

def ismissing(data=_undef):
    return data is _empty

def isempty(data=_undef):
    empty_values = ['', None, [], {}, tuple(), set()]
    return data in empty_values

def isnull(data=_undef):
    return data is None

def prepend_required(context):
    # TODO: import required her
    if not context.has_required:
        context.prepend_processor(~required)

def append_allowempty(context):
    if not context.has_allowempty:
        context.append_processor(~allowempty)

def append_allownull(context):
    if not context.has_allownull:
        context.append_processor(allownull)

class PrimitiveTypeProcessor(Processor):
    def run(self, data, context):
        return is_primitive_type(data, context)

class ArrayTypeProcessor(Processor):
    def run(self, data, context):
        return is_array_type(data, context)

class ObjectTypeProcessor(Processor):
    def run(self, data, context):
        return is_object_type(data, context)

def is_primitive_type(data, context):
    # TODO: handle bytes somehow
    if (utils.is_str(data) or utils.is_numberlike(data) 
        or utils.is_boolean(data) or data is None):
        return data
    # TODO more descriptive message
    raise err.ValidationError(
        'Wrong type provided. Expected Array type.', type(data))

def is_array_type(data, context):
    # ensures that data is None or if not set 
    # otherwise ensures that data is set to a non-dict sequence 
    # then attempts to convert it to a list
    if data is None:
        return None
    if utils.is_iterable(data, exclude_set=True, 
                            exclude_generator=True):
        return list(data)
    # TODO more descriptive message
    raise err.ValidationError(
        'Wrong type provided. Expected Array type.', 
        type(data))

def is_object_type(data, context):
    if data is None:
        return None
    try:
        if utils.is_dict(data):
            return dict(data)
    except:
        pass
    # TODO more descriptive message
    raise err.ValidationError(
        'Wrong type provided. Expected Object type.', 
        type(data))

class polymorphic(object):

    def __init__(self, fnc):
        self._method = fnc
        self._name = fnc.name

    def classmethod(self, fnc):
        self._classmethod = fnc

    """let the descriptor handle the switch between behaviors"""
    def __get__(self, instance, owner):
        if instance is None:
            try:
                return self._classmethod.__get__(owner, owner.__class__)
            except:
                raise VinoError('no class behavior registered for method {}.'
                               .format(self._name))
        else:
            return self._method.__get__(instance, owner)

class BooleanProcessorMeta(type):
    def __invert__(cls):
        """ this allows `BooleanProcessor` classes to return an instance of
        themselves with a data set to the opposite when the bitwise `~` is
        applied on them.
        """
        return cls(not cls.__default__)

    def vino_init(cls, *a, **kw):
        return cls(*a, **kw)


class ProcessorBatch(Processor):
    """ Packs a sequence of processors to apply to a group of items.
    
    How it differs from a RunnerStack: the Stack is an invisible object that is
    intimely tied to its parent Context. It basically serves as a liaison
    between a Context and its Processes. It specializes in managing their
    relationship by altering the latter's configurations and behaviour
    depending on the former's type. You can only have a single RunnerStack
    per Context. It's the Context's all encompassing container of Processes.

    A ProcessorBatch is a useful container that contains multiple Processors
    to be ran on a set of Items from its parent Context (or ProcessorBatch) 
    Unlike RunnerStack you can have multiple ProcessorBatches per Context and
    you can even embed them one into another, at which point the inner Batch
    is applied to items from its parent's subset that pass its qualification.
    """

    def __init__(self, *processors):
        pass
    
    def apply_to(*qualifiers):
        """a qualifier can be many things:
            - a range in the form of a range object or a list: in which case
            the listed validation steps will apply to all items whose index
            falls within the list returned by the range. 
            - a function: which should return True for an item before the 
            validation steps proceed.
        """
        self.qualifiers = qualifiers

    def run(self, data):
        pass

class MandatoryClause:
    # meta properties about the clause
    __clause_mandatory__ = False
    __clause_name__ = None
    __clause_precedence__ = None

    @classmethod # good candidate for a polymorphic method
    def adapt(cls, processor):
        """ /!\ if you expect to work with your processor outside of vino, it's
        probably best not to use this as a decorator.
        """
        adapter = ProcessorAdapter(processor)
        adapter.adapt_clause(cls)
        return adapter

class ProcessorAdapter:
    def __init__(self, fnc):
        self.fnc = fnc

    def __call__(self, *a, **kw):
        return self.fnc(*a, **kw)

    def run(self, *a, **kw):
        return self.fnc.run(*a, **kw)

    def adapt_clause(self, clause_cls):
        self.__clause_name__ = clause_cls.__clause_name__
        self.__clause_mandatory__ = clause_cls.__clause_mandatory__
        self.__clause_precedence__ = clause_cls.__clause_precedence__

class BooleanProcessor(metaclass=BooleanProcessorMeta):
    __default__ = True

    def __init__(self, data=_undef, mirror=_undef):
        if data is _undef:
            data = self.__class__.__default__
        self.data = bool(data)
        self._register_mirror(mirror)
        
    def _register_mirror(self, mirror=_undef):
        if mirror is _undef:
            mirror = self.__class__(not self.data, self)
        self.mirror = mirror


class Required(BooleanProcessor, MandatoryClause):
    __clause_mandatory__ = True
    __clause_name__ = 'required'
    __clause_precedence__ = 0

    def run(self):
        pass

class AllowNull(BooleanProcessor, MandatoryClause):
    __clause_mandatory__ = True
    __clause_name__ = 'allownull'
    __clause_precedence__ = -1

    def run(self):
        pass

class AllowEmpty(BooleanProcessor, MandatoryClause):
    __clause_mandatory__ = True
    __clause_name__ = 'allowempty'
    __clause_precedence__ = -2

    def run(self):
        pass

# aliases
required = Required
allowempty = AllowEmpty
allownull = Required
