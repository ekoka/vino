from vino.processors import validating as vld
from vino import errors as err
import pytest

class TestPrimitiveTypeProcessor:

    def test_run_method_returns_value(s, randstr):
        p = vld.PrimitiveTypeProcessor()
        assert p.run(randstr, None)==randstr

    def test_validates_primitive_type(s):
        p = vld.PrimitiveTypeProcessor()
        assert 1==p.run(1, None)
        assert 1.2==p.run(1.2, None)
        assert None is p.run(None, None)
        assert ""==p.run("", None)
        assert "(- . -)"==p.run("(- . -)", None)
        assert False is p.run(False, None)
        assert True is p.run(True, None)

    def test_raises_ValidationError_on_non_primitives(s):
        p = vld.PrimitiveTypeProcessor()
        err_msg = 'wrong type provided. expected array type'
        with pytest.raises(err.ValidationError) as exc:
            p.run([], None)
        assert err_msg in str(exc.value).lower()
        with pytest.raises(err.ValidationError) as exc:
            p.run(list('abcdef'), None)
        assert err_msg in str(exc.value).lower()
        with pytest.raises(err.ValidationError) as exc:
            p.run({'a': 'e'}, None)
        assert err_msg in str(exc.value).lower()
        #TODO: what happens with byte type

class TestArrayTypeProcessor:
    def test_can_validate_listlike_data(s):
        # here we're just happy that it doesn't raise any errors
        p = vld.ArrayTypeProcessor()
        p.run(list('abcd'), None)
        p.run(tuple('abcd'), None)

    def test_converts_array_and_tuple_data_to_list(s):
        p = vld.ArrayTypeProcessor()
        s = 'abcd'
        for f in [list, tuple]:
            rv = p.run(f(s), None)
            assert rv==list(s)

    def test_accepts_empty_list(s):
        p = vld.ArrayTypeProcessor()
        p.run([], None)

    def test_accepts_None(s):
        p = vld.ArrayTypeProcessor()
        p.run(None, None)

    def test_rejects_sets(s):
        p = vld.ArrayTypeProcessor()
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(set('abcd'), None)
        error = e.value
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is set

    def test_rejects_dict(s):
        p = vld.ArrayTypeProcessor()
        with pytest.raises(err.ValidationError) as e:
            rv = p.run({'a':'a', 'b':'c', 'c':'d'}, None)
        error = e.value
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is dict

    def test_rejects_str(s):
        p = vld.ArrayTypeProcessor()
        with pytest.raises(err.ValidationError) as e:
            rv = p.run('abcd', None)
        error = e.value
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is str


class TestObjectTypeProcessor:
    def test_validation_rv_of_empty_object_is_empty_obj(s):
        p = vld.ObjectTypeProcessor()
        rv = p.run({}, None)
        assert rv=={}

    def test_validation_rv_of_null_object_is_null_by_default(s):
        p = vld.ObjectTypeProcessor()
        rv = p.run(None, None)
        assert rv is None

    def test_validation_rv_has_same_values(s):
        p = vld.ObjectTypeProcessor()
        value = {'a':23, 'b':12}
        rv = p.run(value, None)
        assert rv==value

    def test_validation_rv_is_not_original_object(s):
        p = vld.ObjectTypeProcessor()
        value = {'a':23, 'b':12}
        rv = p.run(value, None)
        assert rv is not value 
        value = {}
        rv = p.run(value, None)
        assert rv is not value 

    def test_validation_rejects_list_type(s):
        p = vld.ObjectTypeProcessor()
        value = ['a',23,'b',12]
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is list

    def test_validation_rejects_tuple_type(s):
        p = vld.ObjectTypeProcessor()
        value = ('a',23, 'b',12)
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is tuple

    def test_validation_rejects_strings(s):
        p = vld.ObjectTypeProcessor()
        value = 'abcdelf'
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is str

    def test_validation_rejects_empty_strings(s):
        p = vld.ObjectTypeProcessor()
        value = ''
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is str

    def test_validation_rejects_empty_list(s):
        p = vld.ObjectTypeProcessor()
        value = []
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is list

    def test_validation_rejects_empty_tuple(s):
        p = vld.ObjectTypeProcessor()
        value = ()
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is tuple
        
    def test_validation_rejects_list_of_tuples(s):
        p = vld.ObjectTypeProcessor()
        value = (('a',23), ('b',12))
        with pytest.raises(err.ValidationError) as e:
            rv = p.run(value, None)
        error = e.value
        assert 'wrong type' in e.value.args[0].lower()
        assert e.value.args[1] is tuple

