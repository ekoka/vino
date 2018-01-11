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

    def qualify(self, index, data):
        if index in self.qualifiers['indexes']:
            return True
        for call in self.qualifiers['calls']:
            if call(index, data):
                return True
        return False

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

    def apply(self, data, runner, context):
        rv = []
        for i,d in enumerate(data):
            if self.qualify(i,d):
                rv.append(runner.run(d, context))
            else:
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

    def qualify(self, key, data):
        if key in self.qualifiers['keys']:
            return True
        for call in self.qualifiers['calls']:
            if call(key, data):
                return True
        return False

    def apply(self, data, runner, context):
        rv = {}
        for k,d in data.items(): 
            if self.qualify(k, d):
                rv[k] = runner.run(d, context)
            else:
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
