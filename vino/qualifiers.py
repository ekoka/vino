from . import utils
from . import errors 

class Qualifier:
    def qualify(self, item, index=None): pass

class ItemQualifierStack:

    def __init__(self, context=None, *qualifiers):
        self.qualifiers = {
            'index': set(),
            'call': [],
        }
        self.context = context

        for q in qualifiers:
            self.add(q)

    def empty(self):
        return not (self.qualifiers['index'] or self.qualifiers['call'])

    def qualify(self, index, data):
        if index in self.qualifiers['index']:
            return True
        for call in self.qualifiers['call']:
            if call(index, data):
                return True
        return False

    def add(self, *qualifiers):
        for qualifier in qualifiers:
            import logging
            logger = logging.getLogger('vino')
            logger.info(qualifier)
            if utils.is_intlike(qualifier):
                self.qualifiers['index'].add(qualifier)
            elif utils.is_iterable(qualifier):
                [self.qualifiers['index'].add(i) for i in qualifier]
            elif callable(qualifier):
                self.qualifiers['call'].append(qualifier)
            else:
                # TODO: more descriptive error
                raise errors.VinoError('Invalid Qualifier')


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
