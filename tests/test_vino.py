import pytest
from vino import errors as err
from vino.api import schema as shm
from vino.processors import validating as vld

class TestVino:
    def test_validate_primitive(s):
        s = shm.prim()
        for v in ['abc', 33, None, True, False]:
            assert v == s.validate(v) 

    def test_accepts_int(s):
        s = shm.prim(vld.isint)
        for v in [33, 29, 0]:
            assert v==s.validate(v)

    def test_rejects_non_int(s):
        s = shm.prim(vld.isint)
        for v in [33.2, 29.1, 0.3]:
            with pytest.raises(err.ValidationErrorStack) as e:
                v==s.validate(v)
            assert 'wrong data type expected int' in str(e.value[0]).lower()

    def test_rejects_int(s):
        s = shm.prim(~vld.isint)
        for v in [33, 29, 0]:
            with pytest.raises(err.ValidationErrorStack) as e:
                v==s.validate(v)
            assert 'should not be an int' in str(e.value[0]).lower()

    def test_accepts_non_int(s):
        s = shm.prim(~vld.isint)
        for v in [33.2, 29.1, 0.3, None, False, 'abc']:
            assert v==s.validate(v)

    def test_obj(s):
        data = {'a': 'b', 'c': 33}
        v = shm.obj(
            shm.prim(~vld.isint).apply_to('a'), 
            shm.prim(vld.isint).apply_to('c'), 
            shm.prim(vld.isint).apply_to('e'), 
        )
        assert data == v.validate(data)

    def test_nested(s, logger):
        data = {'a': 'b', 'c': 33, 'u': {'name': 'michael', 'age':44}}
        user_schm = shm.obj(
            shm.prim(~vld.isint).apply_to('name'),
            shm.prim(vld.isint).apply_to('age')
        )
        data_schm = shm.obj(
            shm.prim(~vld.isint).apply_to('a'),
            shm.prim(vld.isint).apply_to('c'),
            user_schm.apply_to('u'),
        )
        rv = data_schm.validate(data)
        assert rv == data






@pytest.mark.skip
class TestSkip:
    def test_onfail(): assert 0
    def test_cast(): assert 0
    def test_obj(): assert 0
    def test_arr(): assert 0
    def test_nested(): assert 0

        
