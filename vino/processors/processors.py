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
        """ this allows `BooleanProcessor` classes to return a mirror class
        that has is semantically the opposite of their setting.
        """
        try:
            mirror_cls = cls.__mirror_cls__()
        except:
            # TODO: more descriptive
            raise err.VinoError('no mirror class was set')
        return mirror_cls

    def vino_init(cls, *a, **kw):
        return cls(*a, **kw)


class BooleanProcessor(metaclass=BooleanProcessorMeta):
    __default__ = True

    def __init__(self, data=_undef, mirror=_undef):
        if data is _undef:
            data = self.__class__.__default__
        self.data = bool(data)
        
