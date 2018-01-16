from .. import utils as uls
from ..processors import processors as prc
from .. import errors as err

class PrimitiveTypeProcessor(prc.Processor):
    def run(self, data, context):
        return is_primitive_type(data, context)

class ArrayTypeProcessor(prc.Processor):
    def run(self, data, context):
        return is_array_type(data, context)

class ObjectTypeProcessor(prc.Processor):
    def run(self, data, context):
        return is_object_type(data, context)

def is_primitive_type(data, context):
    # TODO: handle bytes somehow
    if (data is uls._undef or uls.is_str(data) or uls.is_numberlike(data)
        or uls.is_boolean(data) or data is None):
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
    if uls.is_iterable(data, exclude_set=True, 
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


class Optional(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'required'
    __mirror_cls__=lambda:Required

    def run(self, data=uls._undef, context=uls._undef):
        if not self.data and data is uls._undef:
            raise err.ValidationError('data is required')
        return data

class Required(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'required'
    __mirror_cls__=lambda:Optional

    def run(self, data=uls._undef, context=uls._undef):
        if self.data and data is uls._undef:
            raise err.ValidationError('data is required')
        return data

class RejectNull(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'null'
    __mirror_cls__ = lambda:AllowNull

    def run(self, data=uls._undef, context=uls._undef):
        if self.data and data is None:
            raise err.ValidationError('data must not be null')
        return data

class AllowNull(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'null'
    __mirror_cls__ = lambda:RejectNull

    def run(self, data=uls._undef, context=uls._undef):
        if not self.data and data is None:
            raise err.ValidationError('data must not be null')
        return data

class RejectEmpty(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'empty'
    __mirror_cls__ = lambda:AllowEmpty

    def run(self, data=uls._undef, context=uls._undef):
        if self.data and data in ((), {}, '', set(), []):
            raise err.ValidationError('data must not be empty')
        return data

class AllowEmpty(prc.BooleanProcessor, MandatoryClause):
    __clause_name__ = 'empty'
    __mirror_cls__=lambda:RejectEmpty

    def run(self, data=uls._undef, context=uls._undef):
        if not self.data and data in ((), {}, '', set(), []):
            raise err.ValidationError('data must not be empty')
        return data

# aliases
required = Required
optional = Optional
allowempty = AllowEmpty
allownull = AllowNull
rejectempty = RejectEmpty
rejectnull = RejectNull
