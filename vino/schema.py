from . import contexts as ctx
from . import qualifiers as qls
from . import utils as uls
from . import errors as err
from .processors import runners as rnr
from .processors import validating as vld
from .processors import marshalling as msh
from .processors import processors as prc


class SchemaBase:
    """
    Schemas are the containing objects where validation and marshalling of 
    JSON data elements are declared and encapsulated. Vino has three types of
    Schemas that correspond to JSON main data types.
        - ObjectTypeSchema: used to declare handling of JSON objects.
        - ArrayTypeSchema: used for JSON arrays. 
        - PrimitiveTypeSchema: used for other JSON supported primitive types,
        including strings, numbers, and null.
    Note that the JSON string must be deserialized to its Python form prior to
    be handed over to a Vino schema for validation. Use your own favorite JSON
    library.

    Schemas are also the more curated way to handle validation, as they assign
    default validators to handle null, missing, or empty data, which when not
    clarified may lead to unexpected, sometimes undesirable, outcomes.

    The more "barebone" alternative to using a Schema is to create your own
    `Context` object.
    """

    def add_mandatory_processors(self, processors):
        """
        Add REQUIRED, EMPTY, NULL processors if missing.
        """
        processors = self.set_required_clause(processors)
        notset = self._get_unset_mandatories(processors)

        for p in prc.MandatoryClause.__mandatory_clauses__: # guarantees the order
            if p in notset:
                method = getattr(self, ''.join(['add_', p, '_clause']))
                processors = method(processors)
        return processors

    def _get_unset_mandatories(self, processors):
        unset = {c for c in prc.MandatoryClause.__mandatory_clauses__}
        for p in processors:
            try:
                unset.remove(p.__clause_name__)
                if not unset:
                    break
            except (KeyError, AttributeError):
                continue
        return unset 

    def set_required_clause(self, processors):
        """
        Move REQUIRED mandatory processor to the head of the series if one
        is present, otherwise add one.
        """
        rv = []
        required = None
        for p in processors:
            try:
                if p.__clause_name__==prc.MandatoryClause.REQUIRED:
                    required = p
                else:
                    rv.append(p)
            except AttributeError:
                rv.append(p)
        if required is None:
            required = vld.required
        return (required,) + tuple(rv)

    def add_empty_clause(self, processors):
        rv = processors + (vld.not_allowempty,)
        return rv

    def add_null_clause(self, processors):
        rv = processors + (vld.allownull,)
        return rv

Schema = SchemaBase


class PrimitiveTypeSchema(SchemaBase, ctx.Context):

    def __init__(self, *processors):
        for p in processors:
            self._assert_no_qualifiers(p)
        processors = self.add_mandatory_processors(processors)
        processors = list(processors)
        # Insert `is_primitive_type` processor in second place after `REQUIRED`
        processors[1:1] = [vld.is_primitive_type] # No.2 
        # `Context` initialization
        super(PrimitiveTypeSchema, self).__init__(*processors)

    def _assert_no_qualifiers(self, processor):
        """
        Ensure that processors within primitive data type validation
        declarations are not declared with a qualifier.

            >>> name = prim(
            ...     # good
            ...     is_str, 
            ...     allownull, 
            ...     allowempty, 
            ...     # not good
            ...     is_str.apply_to('firstname')
            ... )
        """
        try:
            processor[:1]
        except TypeError:
            return 
        raise err.VinoError(
            "Cannot qualify processors inside primitive declarations.")
            
class ArrayTypeSchema(SchemaBase, ctx.Context):

    def __init__(self, *processors):
        # add REQUIRED, EMPTY, NULL processors if missing
        processors = self.add_mandatory_processors(processors)
        processors = list(processors)
        # Insert `is_array_type` processor in second place after `REQUIRED`
        processors[1:1] = [vld.is_array_type] # No.2 
        # `Context` initialization, with an ItemQualifierStack
        super(ArrayTypeSchema, self).__init__(
            *processors, qualifier_stack_cls=qls.ItemQualifierStack)

class ObjectTypeSchema(SchemaBase, ctx.Context):
    
    def __init__(self, *processors):
        # add REQUIRED, EMPTY, NULL processors if missing
        processors = self.add_mandatory_processors(processors)
        processors = list(processors)
        # Insert `is_object_type` processor in second place after `REQUIRED`
        processors[1:1] = [vld.is_object_type] # No.2 
        # `Context` initialization, with an MemberQualifierStack
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
