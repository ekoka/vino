from vino.filters import required, Required as _Req
import pytest
import random

@pytest.fixture
def Req():
    # making sure we can reset it
    keep = _Req.__default__
    yield _Req
    _Req.__default__ = keep

def test_lcase_required_is_ucase_Required(Req):
    assert required is Req

def test_value_set_on_Req_instance_cast_to_bool(Req):
    for i in [0, None, [], {}, '']:
        assert Req(i).value is False
    for i in range(9):
        rnd = random.randint(1, 100)
        assert Req(rnd).value is True

def test_instance_of_Req_created_without_value_sets_it_to_default(Req, logger):
    for i in range(30):
        Req.__default__ = [True, False][random.randint(0, 1)]
        rq = Req()
        assert rq.value==Req.__default__

def test_inversing_Req_class_returns_instance_with_value_set_to_False(Req):
    not_required = ~Req
    assert not_required.value is False

def test_instance_of_Req_created_with_a_mirror_instance(Req):
    required = Req()
    assert isinstance(required.mirror, Req)

def test_mirror_instances_have_opposite_bool_values(Req):
    rnd = [random.randint(1, 100) for i in range(9)]
    for i in [0, None, [], {}, '']+rnd:
        r = Req(i)
        assert isinstance(r.value, bool) 
        assert isinstance(r.mirror.value, bool)
        assert r.value is not r.mirror.value

def test_inversing_Req_class_returns_instance_of_class(Req):
    not_required = ~Req
    assert isinstance(not_required, Req)

def test_instance_from_inversing_Req_class_has_mirror_value(Req):
    not_required = ~Req
    assert not_required.value is not Req.__default__

    #assert not_required.mirror.value is True

