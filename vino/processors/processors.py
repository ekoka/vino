from ..utils import _undef
from .. import errors as err
from .. import utils as uls
import functools

class Processor:
    """
    """

    callbacks = {'default', 'override', 'failsafe'}

    def __init__(self, **kw):
        for action_name in Processor.callbacks:
            action = kw.pop(action_name, None)
            if action:
                self.set_callback(action_name, action)

    def set_callback(self, action_name, action):
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


    @classmethod
    def make_processor(cls, fnc):
        """
        A decorator to equip user-defined functions with the remaining
        Processor interface.
        """
        #def wrapper(**kw):
        #    name = fnc.__name__
        #    fnc.__name__ = 'run'
        #    return type()
        #    pass

#TODO: See if this has a use case within Vino
#class polymorphic:
#    """
#    This class decorates a method and return an object that behaves
#    differently if called from an instance or a class.
#    """
#
#    def __init__(self, fnc):
#        self._method = fnc
#        self._name = fnc.name
#
#    def classmethod(self, fnc):
#        self._classmethod = fnc
#
#    """let the descriptor handle the switch between behaviors"""
#    def __get__(self, instance, owner):
#        if instance is None:
#            try:
#                return self._classmethod.__get__(owner, owner.__class__)
#            except:
#                raise VinoError('no class behavior registered for method {}.'
#                               .format(self._name))
#        else:
#            return self._method.__get__(instance, owner)

class MetaBooleanProcessor(type):
    """
    This metaclass for `BooleanProcessors` automatically provides their class
    (e.g. `AllowNull`, `AllowEmpty`, etc) with a semantically opposite class
    that is returned when the class is queried for its inverse (~Class).

    For instance, the following `~AllowNull` expression would return the
    `AllowNull` class' registered opposite (e.g. `RejectNull`, `NotAllowNull`,
    etc).

        >>> user = obj(
        ...     prim(~AllowNull).apply_to('email')
        ... )

    """

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
        """ 
        Allows the invert operator, when applied on a `BooleanProcessor` class,
        to return another class that would be the "semantic opposite" of that
        `BooleanProcessor`.
        e.g. inverting AllowNull would return the NotAllowNull class.
        >>> ~AllowNull is NotAllowNull
        True
        """
        try:
            return cls.__inverse__
        except:
            # TODO: more descriptive
            raise err.VinoError('no inverse class was set')

    def __call__(cls, **kw):
        if not callable(getattr(cls, 'run', None)):
            # if the class is not an active Processor
            return cls._get_active_processor(**kw)
        #instance = cls.__new__(cls)
        #instance.__init__(flag=flag, **kw)
        #return instance
        return type.__call__(cls, **kw)

    def _get_active_processor(cls, **kw):
        """
        As opposed to "inactive" (or "passive") Processor. An inactive
        Processor relies on its inverse (the 'active" Processor) to do the work
        and simply inverts the parameters given to the active constructor. 
        For instance, instead of having separate `AllowNull` and `NotAllowNull`
        implementations, `NotAllowNull` would simply construct an `AllowNull`
        and invert the default values.

        See some example of inactive `BooleanProcessors` in the 
        `vino.validating` module
        """

        # To be considered active the class must have a `run()` method.
        inverse = cls.__inverse__
        if not callable(getattr(inverse, 'run', None)):
            # Since the present method is called on inactive Processors,
            # having the inverse object also not having a `run()` method
            # indicates two inactive Processors. They're both useless.
            raise err.VinoError('Two inactive Boolean Processors in a '
                                'relationship: {} & {}'.format(cls, inverse))
        try:
            # pop the flag set passed to the inactive Processor's constructor.
            flag = kw.pop('flag')
        except KeyError:
            # flag not in **kw, means we go for default
            flag = cls.__default_value__

        if flag not in cls.__accepted_values__: # will accept 0 and 1
            #TODO: better message
            raise err.VinoError('Expected boolean value, got ', flag)

        # Set inverted bool value on active class
        flag = not flag
        instance = inverse.__new__(inverse)
        instance.__init__(flag=flag, **kw)
        return instance

    def vino_init(cls, **kw):
        return cls(**kw)


class BooleanProcessor(Processor, metaclass=MetaBooleanProcessor):
    __accepted_values__ = (True, False)
    __default_value__ = True

    def __init__(self, **kwargs):
        flag = kwargs.pop('flag', None)
        mapping = kwargs.pop('mapping', None)
        super(BooleanProcessor, self).__init__(**kwargs)
        if flag is None:
            flag = self.__class__.__default_value__

        if flag not in BooleanProcessor.__accepted_values__:
            #TODO: better message
            raise err.VinoError('Expected boolean value, got ', flag)
        self.flag = flag 
        if mapping is not None:
            self.mapping = mapping


    def _resolve_mapping(self, value):
        try:
            return self.mapping[value]
        except AttributeError:
            #TODO: better message
            raise err.ValidationError('no mapping defined')
        except KeyError:
            #TODO: better message
            raise err.ValidationError('value not found in mapping')


class MandatoryClause: # Mixin
    """
    `MandatoryClauses` include the `Require`, `AllowNull`, and `AllowEmpty`
    families of `Processors` (and their related aliases and alternatives: 
    `NotRequired`, `Optional`, `RejectNull`, `NotAllowNull`, etc...)
    When declaring an `Object` validation schema, one of each of the three
    aforementioned families of `Processors` is added as part of the definition
    of the object's properties in the schema. This is done either explicitly
    like:
    
        >>> obj(
        ...     property(required, allownull ,allowempty).apply_to('firstname'),
        ...     ...
        ... )
    
    Or implicitly, if omitted from the declaration:

        >>> obj(
        ...     property().apply_to('firstname'),
        ...     ...
        ... )

    To detect that a `Schema` property was given one of each `MandatoryClauses` it
    probes the property `Schema()` object for the `__clause_name__` attribute.
    """
    # the only accepted clauses
    REQUIRED = 'required'
    EMPTY = 'empty'
    NULL = 'null'
    # a list to preserve the order
    __mandatory_clauses__ = [REQUIRED, EMPTY, NULL] 
    __clause_name__ = None

    @classmethod
    def adapt(cls, processor):
        # TODO: raise an error if this is used directly from MandatoryClause.
        # its intended to be used from one of the mixed-in subclasses. E.g.
        # AllowEmpty.adapt(processor)
        """ 
        This decorator allows to wrap an ordinary function and return a
        `MandatoryClauseAdapter` object that simply behaves like the 
        `MandatoryClause` that adapted it.

            >>> my_allow_null = AllowNull.adapt(my_own_processor)
            >>> obj(
            ...     property(my_allow_null).apply_to('firstname')
            ... )

        If you expect to work with your processor outside of vino, it's
        probably best not to use this with the decorator syntax and stick with.
        """
        adapter = MandatoryClauseAdapter(processor)
        adapter.__clause_name__ = cls.__clause_name__
        return adapter

class MandatoryClauseAdapter:
    def __init__(self, fnc):
        self.fnc = fnc

    def __call__(self, *a, **kw):
        return self.fnc(*a, **kw)

    def run(self, *a, **kw):
        return self.fnc.run(*a, **kw)
