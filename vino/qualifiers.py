from . import utils as uls
from . import errors 

"""
Qualifiers specify to which items or properties a declaration should apply.  

    >>> from vino import obj, arr, prim
    >>> from vino.processors import required, allownull, allowempty, is_str
    >>> user = obj(
    ...     prim(~required, allownull, allowempty, is_str).apply_to(
    ...         'first_name', 
    ...         'last_name', 
    ...         'phone', 
    ...         'email'),
    ...     arr(allowempty, ~allownull,~required).apply_to('technologies'),
    ... )

In the above declaration, the qualifiers are "first_name", "last_name",
"phone", "email", and "technologies".
"""

class Qualifier:
    def qualify(self, item, index=None): pass

class ItemQualifierStack:
    """
    In JSON, this would conceptually be the stack of qualified indices that drives the
    processing of an Array.
    """

    def __init__(self, *qualifiers):
        self.add(*qualifiers)

    @property
    def qualifiers(self):
        """
        The stack of qualifiers. Note that unlike the `callables` stack, the
        stack of `indices` is actually a set, not a list, thus it cannot
        influence the order in which items are processed.

        Items are always processed following the normal flow of indices. If
        you need to break out of that sequence you can declare multiple
        processors and isolate the relevant indices with different qualifiers.

        """
        if not hasattr(self, '_qualifiers'):
            self._qualifiers = {
                'indices': set(),
                'callables': [],
            }
        return self._qualifiers

    def empty(self):
        return not (self.qualifiers['indices'] or self.qualifiers['callables'])


    def add(self, *qualifiers):
        for qualifier in qualifiers:
            if uls.is_intlike(qualifier):
                self.qualifiers['indices'].add(qualifier)
                # when qualifier is integer add to stack of 'indices'
            elif uls.is_iterable(qualifier):
                # when qualifier is iterable add to stack of 'indices' as well
                self.qualifiers['indices'].update(i for i in qualifier)
            elif callable(qualifier):
                # when qualifier is callable add to 'callables'
                self.qualifiers['callables'].append(qualifier)
            else:
                # array structures' qualifiers are limited to 'indices' and
                # 'callables', anything else is an error.
                # TODO: more descriptive error
                raise errors.VinoError('Invalid Qualifier')

    def index_match(self, idx):
        # is the provided index present in the 'indices' stack?
        return idx in self.qualifiers['indices']

    def call_match(self, idx, data):
        # if any of the 'callables' stack qualifiers returns True for the provided  
        # index, return True
        for call in self.qualifiers['callables']:
            if call(idx, data):
                return True

    @classmethod
    def init_matches(cls):
        #TODO: there has to be a better way than using a classmethod for this.
        #TODO: I should clean up all this state/matches business.
        return dict(
            by_index=set(),
            by_call=set(),
            #not_matched=set(),
        )

    def _get_matches(self, state):
        # TODO: When the state has its own class, it should be passed
        # to the qualifier.
        if state.get('matches') is None:
            # None means we're initializing the state for Array type
            state['matches'] = dict(
                by_index=set(),
                by_call=set(),
                #not_matched=set(),
            )
        elif state['matches'].get('by_index') is None:
            # if the state is not None, but the 'by_index' key is not set on 
            # the matches, not even to an empty set, something is off.
            #TODO: better error message
            raise err.VinoError('unstable state')
        return state['matches']

    def apply(self, data, runner, state):
        # TODO: Test
        matches = self._get_matches(state)
        rv = []
        for i,d in enumerate(data): 
            if self.index_match(i):
                matches['by_index'].add(i)
                rv.append(runner.run(d, state))
            elif self.call_match(i, d):
                matches['by_call'].add(i)
                rv.append(runner.run(d, state))
            else:
                #matches['not_matched'].add(i)
                rv.append(d)
        return rv

class MemberQualifierStack:
    """
    In JSON, this would conceptually be the stack of qualifiers that drives the
    processing of an Object.
    It primarily collects keys declared as part of the addition of a processor.
    These keys correspond to the data object's properties to which the
    processor will be applied.
    """

    def __init__(self, *qualifiers):
        self.add(*qualifiers)

    @property
    def qualifiers(self):
        """
        The stack of qualifiers. Note that unlike the `callables` stack, the
        `keys` stack is a set, not a list, thus it cannot influence the
        order in which properties are processed.
        if such control is needed, simply declare processors one after
        the other during Context creation.
        """
        if not hasattr(self, '_qualifiers'):
            self._qualifiers = {
                'keys': set(),
                'callables': [],
            }
        return self._qualifiers

    def add(self, *qualifiers):
        for qualifier in qualifiers:
            if uls.is_str(qualifier):
                # if the qualifier is a string add it to the 'keys' stack.
                self.qualifiers['keys'].add(qualifier)
            elif uls.is_iterable(qualifier):
                [self.qualifiers['keys'].add(i) for i in qualifier]
            elif callable(qualifier):
                self.qualifiers['callables'].append(qualifier)
            else:
                # TODO: more descriptive error
                raise errors.VinoError('Invalid Qualifier')

    def keys_match(self, key):
        return key in self.qualifiers['keys']

    def call_match(self, key, data):
        for call in self.qualifiers['callables']:
            if call(key, data):
                return True

    def _get_matches(self, state):
        # TODO: When the state is part of its own class, it should be passed
        # to the qualifier.
        if state.get('matches') is None:
            # None means we're initializing the state for Object type
            state['matches'] = self.init_matches() 
        elif state['matches'].get('by_key') is None:
            # if not None, but no 'by_key' something is off
            #TODO: better error message
            raise err.VinoError('unstable state')
        return state['matches']

    @classmethod
    def init_matches(cls):
        #TODO: there has to be a better way than using a classmethod for this.
        #TODO: I should clean up all this state/matches business.
        return dict(
            by_key=set(),
            by_call=set(),
            #not_matched=set(),
        )

    def apply(self, data, runner, state):
        matches = self._get_matches(state)
        rv = {}
        for k,value in data.items(): 
            if self.keys_match(k):
                matches['by_key'].add(k)
                rv[k] = runner.run(value, state)
            elif self.call_match(k, value):
                matches['by_call'].add(k)
                rv[k] = runner.run(value, state)
            else:
                #matches['not_matched'].add(k)
                rv[k] = value

        self._process_missing_keys(rv, matches['by_key'], runner, state)
        return rv

    def _process_missing_keys(self, data, matched_keys, runner, state):
        # ensure that all the explicit keys have been dealt with
        qualkeys = self.qualifiers['keys']
        unmatched = qualkeys.difference(matched_keys)
        if unmatched:
            # some keys were explicitly registered, but are missing from the
            # data. Maybe the runner is set up to provide a default value, or
            # maybe it'll just raise a ValidationError. Let's find out.
            default = runner.run(uls._undef, state=state)
            # ok we got here, so it didn't raise an error.
            if not default is uls._undef:
                for k in unmatched:
                    data[k] = default
                    matched_keys.add(k)

class SequenceQualifier(Qualifier):

    def __init__(self, start=0, step=None, stop=None):
        """ specifies a range of items to qualify """
        self. items = self.set_sequence(start, step, stop)

    def set_sequence(self, start, step, stop):
        if is_rangelike(start):
            if not (stop is None is step):
                raise err.VinoError(
                    'Cannot mix range object with additional arguments in '
                    'sequence call.')
            start, stop, step = start.start, start.stop, start.step
        elif is_listlike(start): # we don't want no generators!
            rv = self._list_to_range(start, step)
            
        for n,s in dict(start=start, stop=stop, step=step):
            try:
                s = abs(s)-1 if n=='step' else s
                if not is_intlike(s, positive=True):
                    raise TypeError()
            except TypeError:
                raise err.VinoError(
                    'Invalid {} value given for sequence: {}'.format(n,s))

        return range(start, stop, step)

    def __invert__(self):
        """ switch between qualifier and disqualifier """
        _current = self._qualifier_fnc
        self._qualifier_fnc = {
            self._qualify: self._disqualify,
            self._disqualify:self._qualify}[_current]
        return self

    def _qualify(self, *a, **kw):
        pass

    _qualifier_fnc = _qualify

    def _disqualify(self, *a, **kw):
        pass

seq = sequence = SequenceQualifier
