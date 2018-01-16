import pytest
from vino.api import schema as shm
from vino.processors import validating as  vld
from vino import errors as err

@pytest.fixture
def prim():
    rv = shm.PrimitiveTypeSchema()
    return rv

@pytest.fixture
def arr():
    return shm.ArrayTypeSchema()

class TestPrimitiveTypeSchema:

    def test_adds_primitive_type_processor_first(s, prim):
        assert prim.runners[0]['runner']._raw_processor is vld.is_primitive_type

    def test_adds_required_processor_if_none_found(s, prim):
        assert isinstance(prim.runners[1]['runner']._raw_processor, 
                          vld.required)
        #with pytest.raises(err.ValidationErrorStack) as e:
        #    prim.validate()
        #assert 'data is required' in str(e.value[0])

    def test_adds_rejectempty_processor_if_no_empty_clause_found(s, prim):
        assert isinstance(prim.runners[2]['runner']._raw_processor, 
                          ~vld.allowempty)
        #with pytest.raises(err.ValidationErrorStack) as e:
        #    prim.validate('')
        #assert 'data must not be empty' in str(e.value[0])

    def test_adds_allownull_processor_if_no_null_clause_found(s, prim, mocker):
        assert isinstance(prim.runners[3]['runner']._raw_processor, 
                          vld.allownull)
        #mk_alwnl = mocker.patch.object(vld.allownull, 'run')
        #prim.validate(None)
        #mk_alwnl.assert_called_once_with(None, prim)

    def test_total_number_of_default_validators_is_4(s):
        prim = shm.PrimitiveTypeSchema()
        assert len(prim.runners)==4

    def test_doesnt_add_implicit_required_processor_if_one_provided(s):
        p0 = lambda *a: None
        p1 = vld.required()
        prim = shm.PrimitiveTypeSchema(p0, p1)
        assert len(prim.runners)==5
        assert prim.runners[2]['runner']._raw_processor is p1

    def test_doesnt_add_implicit_allowempty_processor_if_one_provided(s):
        p0 = lambda *a: None
        p1 = vld.allowempty()
        prim = shm.PrimitiveTypeSchema(p0, p1)
        assert len(prim.runners)==5
        # added right after primitive type, required, and p0
        assert prim.runners[3]['runner']._raw_processor is p1

    def test_doesnt_add_implicit_allownull_processor_if_one_provided(s, logger):
        p0 = lambda *a: None
        p1 = vld.rejectnull()
        prim = shm.PrimitiveTypeSchema(p0, p1)
        assert len(prim.runners)==5
        # added right after primitive type, required, and p0,
        # before implicit allowempty.
        assert prim.runners[3]['runner']._raw_processor is p1


#class TestArrayTypeSchema:
#
#    def test_adds_array_type_processor_first(s, arr):
#        assert arr.runners[0]['runner']._raw_processor is vld.is_array_type
