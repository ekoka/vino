from .. import utils as uls
from ..processors import processors as prc
from .. import errors as err

class PrimitiveTypeProcessor(prc.Processor):
    def run(self, data, state):
        return is_primitive_type(data, state)

class ArrayTypeProcessor(prc.Processor):
    def run(self, data, state):
        return is_array_type(data, state)

class ObjectTypeProcessor(prc.Processor):
    def run(self, data, state):
        return is_object_type(data, state)

def is_primitive_type(data, state):
    # TODO: handle bytes somehow
    if (data is uls._undef or uls.is_str(data) or uls.is_numberlike(data)
        or uls.is_boolean(data) or data is None):
        return data
    # TODO more descriptive message
    raise err.ValidationError(
        'Wrong type provided. Expected Array type.', type(data))

def is_array_type(data, state):
    # ensures that data is None or if not set 
    # otherwise ensures that data is set to a non-dict sequence 
    # then attempts to convert it to a list
    if data is None:
        return None
    if uls.is_iterable(data, exclude_set=True, 
                            exclude_generator=True):
        return list(data)
    # TODO more descriptive message
    raise err.ValidationError(
        'Wrong type provided. Expected Array type.', 
        type(data))

def is_object_type(data, state):
    if data is None:
        return None
    try:
        if uls.is_dict(data):
            return dict(data)
    except:
        pass
    # TODO more descriptive message
    raise err.ValidationError(
        'Wrong type provided. Expected Object type.', 
        type(data))

class MandatoryClause:
    __clause_name__ = None

    @classmethod # good candidate for a polymorphic method
    def adapt(cls, processor):
        """ /!\ if you expect to work with your processor outside of vino, it's
        probably best not to use this as a decorator.
        """
        adapter = ProcessorAdapter(processor)
        adapter.__clause_name__ = cls.__clause_name__
        return adapter

class ProcessorAdapter:
    def __init__(self, fnc):
        self.fnc = fnc

    def __call__(self, *a, **kw):
        return self.fnc(*a, **kw)

    def run(self, *a, **kw):
        return self.fnc.run(*a, **kw)

class Optional(prc.BooleanProcessor, MandatoryClause): pass
class Required(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'required'
    __inverse__=Optional

    def __init__(self, *a, **kw):
        # default is a kw only argument
        self.default = kw.pop('default', uls._undef)
        if self.default is not uls._undef:
            if callable(self.default):
                self.default = [default]
            else:
            # TODO: must also allow processors, i.e. check for run() method
            # TODO: should create an `is_processor()` function.
                try:
                    if not self.default:
                        raise TypeError
                    for c in self.default:
                        if not callable(c):
                            raise TypeError
                except TypeError:
                    raise err.VinoError(
                        '"default" must be a callable or a list of callables')

        super(Required, self).__init__(*a, **kw)

    def run(self, data=uls._undef, state=uls._undef):
        if self.flag and data is uls._undef:
            if self.default is not uls._undef:
                for fnc in self.default:
                    data = fnc(data=data, state=state)
            else:
                raise err.ValidationError('data is required')
        return data

class AllowNull(prc.BooleanProcessor, MandatoryClause): pass
class RejectNull(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'null'
    __inverse__ =AllowNull

    def run(self, data=uls._undef, state=uls._undef):
        if self.flag and data is None:
            raise err.ValidationError('data must not be null')
        return data

class AllowEmpty(prc.BooleanProcessor, MandatoryClause): pass
class RejectEmpty(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'empty'
    __inverse__ = AllowEmpty

    def run(self, data=uls._undef, state=uls._undef):
        if self.flag and data in ((), {}, '', set(), []):
            raise err.ValidationError('data must not be empty')
        return data

# aliases
required = Required
optional = Optional
allowempty = AllowEmpty
allownull = AllowNull
rejectempty = RejectEmpty
rejectnull = RejectNull

class isnotint(prc.BooleanProcessor):

    def __init__(self, onfail=None, cast=False, bool_as_int=False):
        self.onfail = onfail
        self.isint = isnotint.__inverse__(cast=cast, bool_as_int=bool_as_int)

    def run(self, data=uls._undef, state=uls._undef):
        try:
            self.isint.run(data)
        except err.ValidationError:
            return data
            #TODO: better message
        raise err.ValidationError('value should not be an integer.')


class isint(prc.BooleanProcessor):
    __clause_name__ = 'int'
    __inverse__ = isnotint

    def __init__(self, onfail=None, cast=False, bool_as_int=False):
        self.onfail = onfail
        self.cast = cast
        self.bool_as_int = bool_as_int

    def run(self, data=uls._undef, state=uls._undef):
        data = self._cast(data)
        if not uls.is_intlike(data, bool_as_int=self.bool_as_int):
            #TODO: better message
            raise err.ValidationError('wrong data type expected int')
        return data

    def _cast(self, data):
        if self.cast: 
            if self.cast is True:
                fnc = int
            else:
                fnc = self.cast
            try:
                return fnc(data)
            except:
                pass
        return data
