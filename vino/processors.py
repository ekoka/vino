_empty = object()

class VinoError(Exception): pass

class polymorphic(object):

    def __init__(self, func):
        self._method = func
        self._name = func.name

    def classmethod(self, func):
        self._classmethod = func

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
        themselves with a value set to the opposite when the bitwise `~` is
        applied on them.
        """
        return cls(not cls.__default__)

    def vino_init(cls, *a, **kw):
        return cls(*a, **kw)

class BooleanProcessor(metaclass=BooleanProcessorMeta):
    __default__ = True

    def __init__(self, value=_empty, mirror=_empty):
        if value is _empty:
            value = self.__class__.__default__
        self.value = bool(value)
        self._register_mirror(mirror)
        
    def _register_mirror(self, mirror=_empty):
        if mirror is _empty:
            mirror = self.__class__(not self.value, self)
        self.mirror = mirror

class Required(BooleanProcessor):
    def run(self):
        pass

class AllowNull(BooleanProcessor):
    def run(self):
        pass

class AllowEmpty(BooleanProcessor):
    def run(self):
        pass

mandatory = required = Required = Mandatory
allowempty = AllowEmpty
allownull = Required
allowmissing = AllowMissing
