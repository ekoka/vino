from .. import utils as uls
from ..processors import processors as prc
from .. import errors as err

class ExtraProperties(prc.Processor):
    __possible_actions__ = ('raise', 'remove', 'ignore')
    def __init__(self, action='remove'):
        if action not in ExtraProperties.__possible_actions__:
            #TODO better message
            raise err.VinoError('Action not recognize')
        self.action = action

    def run(self, data, state):
        try:
            matches = state['matches']
        except (TypeError, KeyError) as e:
            #TODO better message
            raise err.VinoError('processor used in wrong context')

        if self.action=='remove':
            self._remove_if_not_matched(data)
        elif self.action=='raise':
            self._raise_if_not_matched(data)
        # else we 'ignore'
        return data

    def _raise_if_not_matched(self, data):
        for k in matches['not_matched']:
            if k in data:
                #TODO better message
                raise err.ValidationError('Key not in schema')

    def _remove_if_not_matched(self, data):
        for k in matches['not_matched']:
            try:
                data.pop(k)
            except KeyError:
                pass

class MaxLength(prc.Processor):
    def __init__(self, max=-1):
        if not uls.is_intlike(length):
            raise err.VinoError('MaxLength expects positive integer')
        self.max = max

    def run(self, data, state):
        try:
            if self.max<0:
                return data
            if len(data) > self.max:
                return data[:self.max]
        except TypeError:
            #TODO better message
            err.ValidationError('wrong data type')
