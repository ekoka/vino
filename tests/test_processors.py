import pytest
import random

from vino.processors.processors import Processor
from vino import errors as err
from vino import contexts as ctx
from vino import qualifiers as quals

@pytest.mark.testing
class TestProcessor:

    def test_should_take_only_kw_arguments(s):
        """Processor(key=value)
        should only receive kw arguments.
        """
        default = lambda*a,**kw:None
        with pytest.raises(TypeError) as e:
            Processor(default)
        assert ('1 positional argument but 2 were given' 
                in str(e.value).lower())

    def test_if_default_provided_should_set_it(s):
        """p = Processor(default=default)
        if default provided, should set p.default
        """
        default = lambda*a,**kw:None
        p = Processor(default=default)
        assert hasattr(p, 'default')

    def test_if_override_provided_should_set_it(s):
        """p = Processor(override=override)
        if override provided, should set p.override
        """
        override = lambda*a,**kw:None
        p = Processor(override=override)
        assert hasattr(p, 'override')

    def test_if_failsafe_provided_should_set_it(s):
        """p = Processor(failsafe=failsafe)
        if failsafe provided, should set p.failsafe
        """
        failsafe = lambda*a,**kw:None
        p = Processor(failsafe=failsafe)
        assert hasattr(p, 'failsafe')

    def test_set_callback_stores_callback_in_list(s):
        """set_callback('name', callback)
        should store callback in the "name" property.
        """
        cb = lambda*a,**k:None
        p = Processor()
        p.set_callback('name', cb)
        assert hasattr(p, 'name')

    def test_set_callback_stores_callback_in_list(s):
        """set_callback('name', callback)
        should store callback in a list.
        """
        cb = lambda*a,**k:None
        p = Processor()
        p.set_callback('name', cb)
        assert isinstance(p.name, list)

