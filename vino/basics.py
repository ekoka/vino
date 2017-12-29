from . import errors
""" This file describes the schema mappings of JSON's basic types """

class ProcessorRunner:
    def __init__(self, processor):
        if hasattr(processor, 'vino_init'): 
            # calling a constructor if any
            processor = processor.vino_init()
        processor = self._valid_processor(processor)
        self.processor = processor

    def _valid_processor(self, processor):
        if hasattr(processor, 'run'):
            return lambda *a, **kw: processor.run(*a, **kw)
        if callable(processor):
            return processor
        name = (processor.name 
                if hasattr(processor, 'name') 
                else repr(processor))
        raise errors.VinoError('Invalid Processor {}'.format(name))

    def run(value, schema):
        self.processor.run(value, schema)

class RunnerBatch:
    def __init__(self, schema, *processors):
        self.schema = schema
        for p in processors:
            self.runners.append(ProcessorRunner(p))

    def run(self, value):
        for r in self.runners:
            value = r.run(value, self.schema)

class ArrayRunnerBatch:
    def __init__(self, schema, *processors):
        self.schema = schema
        for p in processors:
            if isinstance(p, ItemSchema): # for list of items
                pass
            self.runners.append(ProcessorRunner(p))
#def VinoGraph: pass
#
#def ObjectGraph(VinoGraph): pass
#
#def ArrayGraph(VinoGraph):
#    def __init__(self, schema):

class VinoSchema:
    def __init__(self, name=None, *processors):
        if name is None:
            raise errors.VinoError('None type is not a valid processor.')
        if isinstance(name, str):
            self.name = name
        else:
            self.name = None
            processors = [name]+processors
        self.make_batch(*processors)


class ObjectSchema(VinoSchema): pass
class ObjectPropertySchema(VinoSchema): pass

class BasicSchema(VinoSchema):

    def make_batch(*processors):
        self.batch = RunnerBatch(self, *processors)
        
    def validate(self, value):
        errors = []
        result = None
        for f in self.processors:
            try:
                value = f.run(value)
            else errors.ValidationError as e:
                if e.interrupt_validation: #  
                    raise e
                errors.append(e)
            else AttributeError as e:
                value = f(value, datagraph)
        if errors: 
            raise errors.ErrorCollection(errors)


class ArraySchema(VinoSchema):
    def make_batch(self, *processors):
        for p in processors:
            if p 

class ArrayItemSchema(VinoSchema):
    def make_batch(*processors):
        for p in processors:
            if isinstance(p,):

