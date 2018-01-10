from vino.processors.processors import BooleanProcessor, MandatoryClause
import pytest
import random

@pytest.fixture
def BP():
    class rv(BooleanProcessor): pass
    return rv 

@pytest.fixture
def Mandatory():
    class rv(BooleanProcessor, MandatoryClause):
        __clause_mandatory__ = True
        __clause_name__ = 'random clause'
        __clause_precedence__ = -5
    return rv

def test_value_set_on_BP_instance_cast_to_bool(BP):
    for i in [0, None, [], {}, '']:
        assert BP(i).data is False
    for i in range(9):
        rnd = random.randint(1, 100)
        assert BP(rnd).data is True

def test_instance_of_BP_created_without_value_sets_it_to_default(BP, logger):
    for i in range(30):
        BP.__default__ = [True, False][random.randint(0, 1)]
        rq = BP()
        assert rq.data==BP.__default__

def test_inversing_BP_class_returns_instance_with_value_set_to_False(BP):
    not_bp = ~BP
    assert not_bp.data is False

def test_instance_of_BP_created_with_a_mirror_instance(BP):
    bp = BP()
    assert isinstance(bp.mirror, BP)

def test_mirror_instances_have_opposite_bool_values(BP):
    rnd = [random.randint(1, 100) for i in range(9)]
    for i in [0, None, [], {}, '']+rnd:
        r = BP(i)
        assert isinstance(r.data, bool) 
        assert isinstance(r.mirror.data, bool)
        assert r.data is not r.mirror.data

def test_inversing_BP_class_returns_instance_of_class(BP):
    not_bp = ~BP
    assert isinstance(not_bp, BP)

def test_instance_from_inversing_BP_class_has_mirror_value(BP):
    not_bp = ~BP
    assert isinstance(not_bp.data, bool) 
    assert isinstance(BP.__default__, bool)
    assert not_bp.data is not BP.__default__

    #assert not_bp.mirror.data is True

def test_callable_wrapped_by_MandatoryClause_acquires_clause_attr(Mandatory):
    M = Mandatory
    @M.adapt
    def someuserdefinedfnc(): pass
    assert someuserdefinedfnc.__clause_name__==M.__clause_name__
    assert someuserdefinedfnc.__clause_precedence__==M.__clause_precedence__
    assert someuserdefinedfnc.__clause_mandatory__==M.__clause_mandatory__

def test_processor_wrapped_by_MandatoryClause_keeps_same_api(Mandatory):
    M = Mandatory
    @M.adapt
    def userdefinedfnc():
        return 'abc 123'
    assert userdefinedfnc()=='abc 123'
    class userdefinedcls:
        def run(self):
            return 'abc 123'
    ud = M.adapt(userdefinedcls())
    assert ud.run()=='abc 123'
