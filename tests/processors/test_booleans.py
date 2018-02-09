from vino.processors import processors as prc
from vino.processors import validating as vld
from vino import errors as err
from vino import utils as uls 
import pytest
import random

@pytest.fixture
def BP():
    class BoolProc(prc.BooleanProcessor): pass
    return BoolProc 

@pytest.fixture
def Inverses():
    class YesCls(prc.BooleanProcessor): pass
    class NoCls(prc.BooleanProcessor):
        __clause_name__ = 'invert'
        __inverse__ = YesCls

    return YesCls, NoCls

@pytest.fixture
def Mandatory():
    class rv(prc.BooleanProcessor, vld.MandatoryClause):
        __clause_name__ = 'random clause'
    return rv

class TestBooleanProcessor:
    def test_inversing_BP_class_returns_inverse_class(s, Inverses):
        Y, N = Inverses
        assert N is ~Y
        assert ~N is Y

    def test_BP_cls_has_default_inverse_if_one_not_explicitly_declared(s, BP):
        InvBP = ~BP

    def test_name_of_auto_inverse_cls_starts_with_Not(s, BP):
        InvBP = ~BP
        assert InvBP.__name__ == 'Not' + BP.__name__

    def test_two_inactive_processors_in_relationship_cannot_instantiate(
            s, Inverses):
        Y, N = Inverses
        with pytest.raises(err.VinoError) as e:
            Y()
        assert 'two inactive' in str(e.value).lower()
        with pytest.raises(err.VinoError) as e:
            N()
        assert 'two inactive' in str(e.value).lower()

    def test_inactive_processor_delegates_to_its_active_counterpart(
            s, Inverses):
        Y, N = Inverses
        # Y activated by giving it a run() method
        Y.run = lambda *a:None
        n = N()
        assert isinstance(n, Y)

    def test_can_have_two_active_processors_in_relationship(s, Inverses):
        Y, N = Inverses
        Y.run = lambda *a: 'yes'
        N.run = lambda *a: 'no'
        y = Y()
        assert y.run('somevalue') == 'yes'
        n = N()
        assert n.run('somevalue') == 'no'
        assert ~Y is N
        assert ~N is Y

    def test_wrong_value_set_on_instance_raises_error(s, BP):
        BP.run = lambda *a: a[0]
        for i in [None, [], {}, '', 2]:
            with pytest.raises(err.VinoError) as e:
                BP(flag=i)
            assert 'expected bool' in str(e.value).lower()

    def test_instance_created_with_default_value(s, BP):
        BP.run = lambda *a:None
        for i in range(30):
            BP.__default_value__ = [True, False][random.randint(0, 1)]
            rq = BP()
            assert rq.flag==BP.__default_value__

    def test_callable_wrapped_by_MandatoryClause_acquires_clause_attr(
            s, Mandatory):
        M = Mandatory
        @M.adapt
        def someuserdefinedfnc(): pass
        assert someuserdefinedfnc.__clause_name__==M.__clause_name__


class TestMandatoryProcessors:
    def test_processor_wrapped_by_MandatoryClause_keeps_same_api(s, Mandatory):
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

    def test_aliases(s):
        assert vld.required is vld.Required
        assert vld.optional is vld.Optional
        assert vld.allownull is vld.AllowNull
        assert vld.rejectnull is vld.RejectNull
        assert vld.allowempty is vld.AllowEmpty
        assert vld.rejectempty is vld.RejectEmpty

    def test_inverses(s):
        assert ~vld.required is vld.optional
        assert ~vld.optional is vld.required
        assert ~vld.allownull is vld.rejectnull
        assert ~vld.rejectnull is vld.allownull
        assert ~vld.allowempty is vld.rejectempty
        assert ~vld.rejectempty is vld.allowempty

class TestRequiredProcessor: 

    def test_required_rejects_absent_value(s):
        v = vld.required()
        with pytest.raises(err.ValidationError) as e:
            v.run()
        assert 'data is required' in str(e.value)
            
    def test_not_optional_rejects_absent_value(s):
        v = vld.optional(flag=False)
        with pytest.raises(err.ValidationError) as e:
            v.run()
        assert 'data is required' in str(e.value)

    def test_not_required_accepts_absent_value(s):
        v = vld.required(flag=False)
        rv = v.run()
        assert rv is uls._undef

    def test_optional_accepts_absent_value(s):
        v = vld.optional()
        rv = v.run()
        assert rv is uls._undef

class TestNullProcessor:
    def test_rejectnull(s):
        v = vld.rejectnull()
        with pytest.raises(err.ValidationError) as e:
            v.run(None)
        assert 'must not be null' in str(e.value)

    def test_allownull(s):
        v = vld.allownull()
        assert v.run(None) is None

    def test_allownull_is_rejectnull_set_to_false(s):
        v = vld.allownull()
        assert isinstance(v, vld.rejectnull)
        assert v.flag is False

    def test_allownull_set_to_false_is_rejectnull_set_to_true(s):
        v = vld.allownull(flag=False)
        assert isinstance(v, vld.rejectnull)
        assert v.flag is True

    def test_rejectnull_accepts_empty_and_false_values(s):
        v = vld.allownull(flag=False)
        for d in ['',{},[],(),set(),False,0]:
            assert v.run(d)==d

class TestEmptyProcessor:
    def test_rejectempty(s):
        v = vld.rejectempty()
        for d in ['',{},[],(),set()]:
            with pytest.raises(err.ValidationError) as e:
                v.run(d)
            assert 'must not be empty' in str(e.value)

    def test_allowempty(s):
        v = vld.rejectempty(flag=False)
        for d in ['',{},[],(),set()]:
            assert v.run(d)==d

    def test_allowempty_is_rejectempty_set_to_False(s):
        v = vld.allowempty()
        assert isinstance(v, vld.rejectempty)
        assert v.flag is False

    def test_allowempty_set_to_false_is_rejectempty(s):
        v = vld.allowempty(flag=False)
        assert isinstance(v, vld.rejectempty)
        assert v.flag is True

    def test_rejectempty_accepts_None_and_False_values(s):
        v = vld.allowempty(flag=False)
        for d in [None,False,0]:
            assert v.run(d)==d
