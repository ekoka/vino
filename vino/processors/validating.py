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
        'Wrong data type. Expected: Primitive (string, boolean, number).'
        ' Got: "{}"'.format(
            type(data).__name__))

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
        'Wrong data type. Expected: Array. Got "{}"'.format(
        type(data).__name__))

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
        'Wrong data type. Expected: Object. Got "{}"'.format( 
        type(data).__name__))


"""
It may not be obvious that two seemingly related processors are not, in fact,
inverse of one another. Consider the hypothetical processor 'is_false' which 
tests that an item is set specifically to `False`. Consider a different
processor `is_true`, which for its part tests that value is specifically
`True`. At first glance they seem to represent the inverse of one another, but
the consider that a more accurate inverse of `is_true` would, in fact, be an 
`isnot_true` processor, which would simply test that its inverse returns fails.

In other situations, however, two processors may indeed just be semantic
opposite of one another. Consider the `optional` processor, which is really
just another way of specifying that something  is `not_required`. Likewise the
inverse of `optional`, `not_optional` is an alias for `required`.

When creating a `BooleanProcessors` although it's adviseable to let Vino
implicitly create the inverse class, it's possible to explicitly do so
yourself.  

If you want to let Vino do the work, only one of the classes needs to be
created. The `MetaBooleanProcessor` will create the inverse formalize the
association. 

One of the BooleanProcessor or its inverse *must* declare a `run()` method, or
an error will be raised as both processors will be considered inactive.

Also see the definition of `MetaBooleanProcessor` which intervenes during the
creation of these classes to attach them to their inverse.

The `MandatoryClauses` are used by Vino's `Schema` to curate validation Context
creation. The `Schema` ensures that cases where data is either null, missing,
or blank are accounted for through the automatic insertion of a processor for
each of the 'REQUIRED', 'NULL' and 'EMPTY' families of mandatory Processors
when they're found to be missing from a `Schema` declaration.
"""

class Optional(prc.BooleanProcessor, prc.MandatoryClause): pass
class Required(prc.BooleanProcessor, prc.MandatoryClause):
    __clause_name__ = prc.MandatoryClause.REQUIRED
    __inverse__=Optional

    def run(self, data=uls._undef, state=None):
        if self.flag and data is uls._undef:
            raise err.ValidationError('data is required')
        return data

class AllowNull(prc.BooleanProcessor, prc.MandatoryClause): pass
class NotAllowNull(prc.BooleanProcessor, prc.MandatoryClause):
    __clause_name__ = prc.MandatoryClause.NULL
    __inverse__ =AllowNull

    def run(self, data=uls._undef, state=None):
        if self.flag and data is None:
            raise err.ValidationError('data must not be null')
        return data

class AllowEmpty(prc.BooleanProcessor, prc.MandatoryClause): pass
class NotAllowEmpty(prc.BooleanProcessor, prc.MandatoryClause):
    __clause_name__ = prc.MandatoryClause.EMPTY
    __inverse__ = AllowEmpty

    def run(self, data=uls._undef, state=None):
        if self.flag and data in ((), {}, '', set(), []):
                raise err.ValidationError('data must not be empty')
        return data

# aliases
not_optional = required = Required
not_required = optional = Optional
allowempty = AllowEmpty
allownull = AllowNull
not_allowempty = NotAllowEmpty 
not_allownull = NotAllowNull

#TODO: better error messages
class isnot_int(prc.BooleanProcessor): pass
class is_int(prc.BooleanProcessor):
    __clause_name__ = 'int'
    __inverse__ = isnot_int

    def run(self, data=uls._undef, state=None):
        if data is None or data is uls._undef:
            # do not handle special cases, leave them to other specialized
            # processors.
            return data
        if self.flag:
            if not uls.is_intlike(data, bool_as_int=False):
                raise err.ValidationError('Wrong data type. Expected: "int"')
        else:
            if uls.is_intlike(data, bool_as_int=False):
                raise err.ValidationError(
                    'Wrong data type. Not expected: "int"')
        return data

class isnot_str(prc.BooleanProcessor): pass
class is_str(prc.BooleanProcessor):
    __clause_name__ = 'str'
    __inverse__ = isnot_str

    def run(self, data=uls._undef, state=None):
        if data is None or data is uls._undef:
            # do not handle special cases, leave them to other specialized
            # processors.
            return data
        if self.flag: 
            if not uls.is_str(data):
                raise err.ValidationError('Wrong data type. Expected: "str"')
        else:
            if uls.is_str(data):
                raise err.ValidationError(
                    'Wrong data type. Not expected: "str"')
        return data


__all__ = [
    'required', 'optional', 'allownull', 'allowempty', 'is_int', 'is_str',
]
