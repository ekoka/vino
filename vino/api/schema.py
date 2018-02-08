from .. import contexts as ctx
from .. import qualifiers as qls
from .. import utils as uls
from .. import errors as err
from ..processors import runners as rnr
from ..processors import validating as vld
from ..processors import marshalling as msh


class Schema:

    __mandatory_clauses__ = ('required', 'empty', 'null')
    
    def add_mandatory_processors(self, processors):
        inactive = self._inactive_mandatories(processors)
        for p in Schema.__mandatory_clauses__: # guarantees the order
            if p in inactive:
                method = getattr(self, 'add_'+p+'_clause')
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

    def add_required_clause(self, processors):
        rv = (vld.required,) + processors
        return rv

    def add_empty_clause(self, processors):
        rv = processors + (vld.rejectempty,)
        return rv

    def add_null_clause(self, processors):
        rv = processors + (vld.allownull,)
        return rv


class PrimitiveTypeSchema(Schema, ctx.Context):

    def __init__(self, *processors):
        for p in processors:
            self._assert_no_qualifiers(p)
        processors = self.add_mandatory_processors(processors)
        processors = list(processors)
        processors[1:1] = [vld.is_primitive_type] # No.2 
        super(PrimitiveTypeSchema, self).__init__(*processors)

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
        processors = list(processors)
        processors[1:1] = [vld.is_array_type] # No.2 
        super(ArrayTypeSchema, self).__init__(
            *processors, qualifier_stack_cls=qls.ItemQualifierStack)

class ObjectTypeSchema(Schema, ctx.Context):
    
    def __init__(self, *processors):
        processors = self.add_mandatory_processors(processors)
        processors = list(processors)
        processors[1:1] = [vld.is_object_type] # No.2 
        super(ObjectTypeSchema, self).__init__(
            *processors, qualifier_stack_cls=qls.MemberQualifierStack)


    def run(self, *a, **kw):
        pre_rv = super(ObjectTypeSchema, self).run(*a, **kw)
        try:
            return {k:v for k,v in pre_rv.items() if v is not uls._undef}
        except AttributeError:
            return pre_rv




prim = PrimitiveTypeSchema
arr = ArrayTypeSchema
obj = ObjectTypeSchema
