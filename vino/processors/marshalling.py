from .. import utils as uls
from ..processors import processors as prc
from .. import errors as err

def to_str(data, state):
    try:
        return str(data)
    except:
        # do nothing on failure
        pass
    return data

def to_int(data, state):
    try:
        return int(data)
    except:
        # do nothing on failure
        pass
    return data


class UnmatchedProperties(prc.Processor):
    # TODO: Test
    """
    This processor handles properties that although present in an object to
    validate, have not been matched by a declaration in the schema. The choices
    of action are: 'raise' an error (fail the validation), 'remove' the extra
    properties, or 'ignore' the properties (leave them in the resulting data).

    Be aware that this processor works by exploring the properties that were
    so far matched in the `Context` it is applied to.
    """
    __possible_actions__ = ('raise', 'remove', 'ignore')
    def __init__(self, action='remove'):
        if action not in UnmatchedProperties.__possible_actions__:
            #TODO better message
            raise err.VinoError('Action not recognize')
        self.action = action

    def run(self, data, state):
        try:
            matches = state['matches']
        except (TypeError, KeyError) as e:
            #TODO better message
            raise err.VinoError('processor used in wrong context')

        for k in self._not_matched(data, matches):
            if self.action=='remove':
                #data.pop(k, None)
                data[k] = uls._undef
            elif self.action=='raise':
                #TODO better message
                raise err.ValidationError('Key not in schema')
        # else we 'ignore'
        return data

    def _not_matched(self, data, matches):
        # TODO: there must be a better way to identify unmatched items. 
        # The current method only traces items that are matched by keys, not
        # by function calls. It would effectively count as unmatched keys that
        # are successfully qualified by functions.
        matches = matches.get('by_key', set([])).union(matches.get('by_call', set([])))
        for k in data:
            if k not in matches:
                yield k

unmatched_properties = UnmatchedProperties

class MaxLength(prc.Processor):
    # TODO: Test
    """
    This processor limits array-like or string-like data to the specified
    maximum.  
    """
    def __init__(self, maxlength=-1):
        if not uls.is_intlike(maxlength):
            raise err.VinoError('MaxLength expects positive integer')
        self.maxlength = maxlength

    def run(self, data, state):
        try:
            if self.maxlength<0:
                return data
            #if len(data) > self.maxlength:
            return data[:self.maxlength]
        except TypeError:
            #TODO better message
            err.ValidationError('wrong data type')

maxlength = MaxLength

__all__ = ['maxlength', 'unmatched_properties']
