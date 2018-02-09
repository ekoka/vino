from ..utils import _undef
from .. import errors as err
from .. import utils
import functools

class Processor:

    def __init__(self, **kw):
        for action_name in ('default', 'override', 'failsafe'):
            action = kw.pop(action_name, None)
            self.set_callback(action_name, action)

    def set_callback(self, action_name, action):
        if action is not None:
            if callable(action):
                action = [action]
            else:
            # TODO: must also allow processors, i.e. check for run() method
            # TODO: should create an `is_processor()` function.
                try:
                    if not action:
                        raise TypeError
                    for c in action:
                        if not callable(c):
                            raise TypeError
                except TypeError:
                    raise err.VinoError(
                        '"{}" must be a callable or a '
                        'list of callables'.format(action_name))
            setattr(self, action_name, action)

    def run_override(self, data=_undef, state=_undef):
        override = getattr(self, 'override', None)
        if override:
            for fnc in override:
                data = fnc(data=data, state=state)
        return data

    def run_default(self, data=_undef, state=_undef):
        default = getattr(self, 'default', None)
        if default:
            for fnc in default:
                data = fnc(data=data, state=state)
        return data

    def run_failsafe(self, data=_undef, state=_undef):
        failsafe = getattr(self, 'failsafe', None)
        if failsafe:
            for fnc in failsafe:
                data = fnc(data=data, state=state)
            return data
        return _undef

    def save_or_fail(self, data=_undef, state=_undef, message=None):
        rv = self.run_failsafe(data, state)
        if rv is _undef:
            if message is None:
                message = 'validation failed'
            raise err.ValidationError(message)
        return rv

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

    def __new__(mtcls, clsname, parents, attrs):
        cls = type.__new__(mtcls, clsname, parents, attrs)
        # get declared inverse and clause, if any
        inverse = attrs.get('__inverse__')
        clause_name = attrs.get('__clause_name__')

        # if no inverse, create one
        if inverse is None:
            inverse_name = 'Not'+clsname
            # neuter automatic inverse
            inv_attrs = {'__qualname__':inverse_name, 
                         '__module__':attrs['__module__']}
            inverse = type.__new__(mtcls, inverse_name, parents, inv_attrs)
            cls.__inverse__ = inverse

        # update inverse
        inverse.__inverse__ = cls
        inverse.__clause_name__ = clause_name

        return cls

    def __invert__(cls):
        """ this allows `BooleanProcessor` classes to return an inverse class
        that has is semantically the opposite of their setting.
        """
        try:
            inverse = cls.__inverse__
        except:
            # TODO: more descriptive
            raise err.VinoError('no inverse class was set')
        return inverse

    def __call__(cls, **kw):
        if not callable(getattr(cls, 'run', None)):
            return cls._get_active_object(**kw)
        return type.__call__(cls, **kw)

    def _get_active_object(cls, **kw):
        # to be considered active the class must have a `run()` method
        inverse = cls.__inverse__
        if not callable(getattr(inverse,'run', None)):
            raise err.VinoError('Two inactive Boolean Processors in one '
                                'relationship.')
        try:
            flag = kw.pop('flag')
        except KeyError:
            # flag not in **kw, means we go for default
            flag = cls.__default_value__

        if flag not in cls.__accepted_values__: # will accept 0 and 1
            #TODO: better message
            raise err.VinoError('Expected boolean value, got ', flag)

        # we switch class and bool value
        flag = not flag
        # create instance
        rv = inverse.__new__(inverse)
        rv.__init__(flag=flag, **kw)
        return rv

    def vino_init(cls, **kw):
        return cls(**kw)


class BooleanProcessor(Processor, metaclass=BooleanProcessorMeta):
    __accepted_values__ = (True, False)
    __default_value__ = True

    def __init__(self, **kwargs):
        flag = kwargs.pop('flag', _undef)
        mapping = kwargs.pop('mapping', None)
        if flag is _undef:
            flag = self.__class__.__default_value__

        if flag not in BooleanProcessor.__accepted_values__:
            #TODO: better message
            raise err.VinoError('Expected boolean value, got ', flag)
        self.flag = flag 
        if mapping is not None:
            self.mapping = mapping

        super(BooleanProcessor, self).__init__(**kwargs)

    def _resolve_mapping(self, value):
        try:
            return self.mapping[value]
        except AttributeError:
            #TODO: better message
            raise err.ValidationError('no mapping defined')
        except KeyError:
            #TODO: better message
            raise err.ValidationError('value not found in mapping')
