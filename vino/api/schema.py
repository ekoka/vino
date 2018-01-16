from .. import contexts as ctx
from .. import qualifiers as qls
from .. import utils as uls
from .. import errors as err
from ..processors import runners as rnr
from ..processors import validating as vld
from ..processors import marshalling as msh


class Schema:

    __mandatory_clauses__ = ('required', 'allowempty', 'allownull')
    
    def add_mandatory_processors(self, processors):
        inactive = self._inactive_mandatories(processors)
        for p in Schema.__mandatory_clauses__: # guarantees the order
            if p in inactive:
                method = getattr(self, 'add_'+p)
                processors = method(processors)
        return processors

    def _inactive_mandatories(self, processors):
        mandatory_clauses = {c:None for c in Schema.__mandatory_clauses__}
        for p in processors:
            try:
                mandatory_clauses.pop(p.__clause_name__)
                if not mandatory_clauses:
                    break
            except (KeyError, AttributeError):
                continue
        return set(mandatory_clauses)

    def add_required(self, processors):
        rv = (vld.required,) + processors
        return rv

    def add_allowempty(self, processors):
        rv = processors + (~vld.allowempty,)
        return rv

    def add_allownull(self, processors):
        rv = processors + (vld.allownull,)
        return rv

class PrimitiveTypeSchema(Schema, ctx.Context):

    def __init__(self, *processors):
        for p in processors:
            self._assert_no_qualifiers(p)
        processors = self.add_mandatory_processors(processors)
        processors = (vld.is_primitive_type,) + processors
        #super(ctx.Context, self).__init__(*processors)
        ctx.Context.__init__(self, *processors)

    def _assert_no_qualifiers(self, processor):
        try:
            processor[:1]
        except TypeError:
            return 
        raise err.VinoError(
            "Cannot qualify a processor applied to a primitive values.")
            
class ArrayTypeSchema(Schema, ctx.Context):

    def __init__(self, *processors):
        processors = self.add_mandatory_processors(processors)
        processors = (vld.is_array_type,) + processors
        super(ctx.Context, self).__init__(
            *processors, qualifier_stack_cls=qls.ItemQualifierStack)

class ObjectTypeSchema(Schema, ctx.Context):
    
    def __init__(self, *processors):
        processors = self.add_mandatory_processors(processors)
        processors = (vld.is_array_type,) + processors
        super(ctx.Context, self).__init__(
            *processors, qualifier_stack_cls=qls.MemberQualifierStack)


