from . import utils
from . import errors 

class Qualifier:
    def qualify(self, item, index=None): pass

class ItemQualifierStack:

    def __init__(self, *qualifiers):
        self.add(*qualifiers)

    @property
    def qualifiers(self):
        if not hasattr(self, '_qualifiers'):
            self._qualifiers = {
                'indexes': set(),
                'calls': [],
            }
        return self._qualifiers

    def empty(self):
        return not (self.qualifiers['indexes'] or self.qualifiers['calls'])


    def add(self, *qualifiers):
        for qualifier in qualifiers:
            if utils.is_intlike(qualifier):
                self.qualifiers['indexes'].add(qualifier)
            elif utils.is_iterable(qualifier):
                [self.qualifiers['indexes'].add(i) for i in qualifier]
            elif callable(qualifier):
                self.qualifiers['calls'].append(qualifier)
            else:
                # TODO: more descriptive error
                raise errors.VinoError('Invalid Qualifier')

    def index_match(self, idx):
        return idx in self.qualifiers['indexes']

    def call_match(self, idx, data):
        for call in self.qualifiers['calls']:
            if call(idx, data):
                return True

    def _get_matches(self, state):
        # TODO: When the state is part of its own class, it should be passed
        # to the qualifier.
        if state.get('matches') is None:
            # None means we're initializing the state for Array type
            state['matches'] = dict(
                by_index=set(),
                by_call=set(),
                not_matched=set(),
            )
        elif state['matches'].get('by_index') is None:
            #TODO: better error message
            raise err.VinoError('unstable state')
        return state['matches']

    def apply(self, data, runner, state):
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
                matches['not_matched'].add(i)
                rv.append(d)
        return rv

class MemberQualifierStack:

    def __init__(self, *qualifiers):
        self.add(*qualifiers)

    @property
    def qualifiers(self):
        if not hasattr(self, '_qualifiers'):
            self._qualifiers = {
                'keys': set(),
                'calls': [],
            }
        return self._qualifiers

    def add(self, *qualifiers):
        for qualifier in qualifiers:
            if utils.is_str(qualifier):
                self.qualifiers['keys'].add(qualifier)
            elif utils.is_iterable(qualifier):
                [self.qualifiers['keys'].add(i) for i in qualifier]
            elif callable(qualifier):
                self.qualifiers['calls'].append(qualifier)
            else:
                # TODO: more descriptive error
                raise errors.VinoError('Invalid Qualifier')

    def keys_match(self, key):
        return key in self.qualifiers['keys']

    def call_match(self, key, data):
        for call in self.qualifiers['calls']:
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
            not_matched=set(),
        )

    def apply(self, data, runner, state):
        matches = self._get_matches(state)
        rv = {}
        for k,d in data.items(): 
            if self.keys_match(k):
                matches['by_key'].add(k)
                rv[k] = runner.run(d, state)
            elif self.call_match(k, d):
                matches['by_call'].add(k)
                rv[k] = runner.run(d, state)
            else:
                matches['not_matched'].add(k)
                rv[k] = d
        return rv


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
