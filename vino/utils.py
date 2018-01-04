# sentinel
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

def is_intlike(i, positive=False):
    try:
        [0][i]
        return i>=0 if positive else True
    except IndexError:
        return True
    except TypeError:
        return False

def is_iterable(value,
        exclude_generator=False,
        exclude_set=False,
        exclude_dict=True,
        exclude_str=True,
        exclude_bytes=True):
    if not hasattr(value, '__iter__'):
        return False
    if exclude_generator and hasattr(value, 'close'):
        return False
    if exclude_dict and hasattr(value, 'get'):
        return False
    if exclude_str and hasattr(value, 'encode'):
        return False
    if exclude_bytes and hasattr(value, 'decode'):
        return False
    return True

def is_boolean(value):
    return value in (True, False)

def is_str(value):
    return hasattr(value, 'encode')

def is_bytestring(value):
    return hasattr(value, 'decode')

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
