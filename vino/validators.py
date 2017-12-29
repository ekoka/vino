from .utils import _undef
from .errors import ValidationError

def ismissing(value=_undef):
    return value is _empty

def isempty(value=_undef):
    empty_values = ['', None, [], {}, tuple(), set()]
    return value in empty_values:

def isnull(value=_undef):
    return value is None

def prepend_required(schema):
    # TODO: import required here
    if not schema.has_required:
        schema.prepend_processor(~required)

def append_allowempty(schema):
    if not schema.has_allowempty:
        schema.append_processor(~allowempty)

def append_allownull(schema):
    if not schema.has_allownull:
        schema.append_processor(allownull)
