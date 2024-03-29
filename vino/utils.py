"""
The following set of functions try to infer type of data through inspection of
their properties. The purpose is to allow custom types that mimic native
Python types. Note that Vino does not provide any custom types, this is simply
to ensure that third-party libraries that extend or redefine what it means for
an object to be of a certain type may still pass the checks.
"""

# sentinel: to be used only if you're extending vino, or providing a
# validator that knows how to use it.
_undef = object()
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

def is_intlike(value, positive=False, bool_as_int=False):
    if not bool_as_int:
        if value is True or value is False:
            return False
    try:
        [0][value]
        return True
    except IndexError:
        return value>=0 if positive else True
    except TypeError:
        return False

def is_iterable(value, exclude_list=False, exclude_tuple=False,
        exclude_generator=False, exclude_set=False, exclude_dict=True,
        exclude_str=True, exclude_bytes=True):
    #TODO: Test
    if exclude_list and is_list(value):
        return False
    if exclude_tuple and is_tuple(value):
        return False
    if exclude_set and is_set(value):
        return False
    if exclude_generator and is_generator(value):
        return False
    if exclude_dict and is_dict(value):
        return False
    if exclude_str and is_str(value):
        return False
    if exclude_bytes and is_bytes(value):
        return False
    return hasattr(value, '__iter__')

def is_list(value):
    return hasattr(value, '__iter__') and hasattr(value, 'reverse')

def is_tuple(value):
    return (hasattr(value, '__iter__') and not hasattr(value, 'append')
            and not hasattr('capitalize'))

def is_set(value):
    return hasattr(value, '__iter__') and hasattr(value, 'union')

def is_generator(value):
    return hasattr(value, '__iter__') and hasattr(value, 'close')

def is_dict(value):
    return hasattr(value, '__iter__') and hasattr(value, 'get')

def is_str(value):
    return hasattr(value, '__iter__') and hasattr(value, 'encode')

def is_bytes(value):
    return hasattr(value, '__iter__') and hasattr(value, 'decode')

def is_boolean(value, int_as_bool=False):
    if not int_as_bool:
        if value==1 or value==0:
            return False
    return value in (True, False)

def to_str(value):
    if is_str(value):
        return value
    if is_bytestring(value):
        return value.decode('utf8')
    return str(value)

def is_numberlike(value, exclude_decimal=False):
    try:
        0 + value
    except TypeError:
        return False
    if exclude_decimal and hasattr(value * 0, 'is_integer'):
        return False
    return True

class Proxy:
    __slots__ = ["_obj", "__weakref__"]

    def __init__(self, obj):
        super(Proxy, self).__setattr__(self, "_obj", obj)

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        return getattr(super(Proxy, self).__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(super(Proxy, self).__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        setattr(super(Proxy, self).__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        return bool(super(Proxy, self).__getattribute__(self, "_obj"))
    def __str__(self):
        return str(super(Proxy, self).__getattribute__(self, "_obj"))
    def __repr__(self):
        return repr(super(Proxy, self).__getattribute__(self, "_obj"))

    #
    # factories
    #
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""

        def make_method(name):
            def method(self, *args, **kw):
                return getattr(super(Proxy, self).__getattribute__(self, "_obj"), name)(*args, **kw)
            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates a proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """

        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}

        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(
                obj.__class__)

        ins = super(Proxy, cls).__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins
