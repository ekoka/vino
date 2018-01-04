class VinoError(Exception): pass

class ValidationError(Exception):
    interrupt_validation = False
    def __init__(self, msg, interrupt_validation=False, *a, **kw): 
        a = (msg,)+a
        super(ValidationError, self).__init__(*a, **kw)
        self.interrupt_validation = interrupt_validation

class ValidationErrorStack(ValidationError):
    def __append__(self, error):
        if not hasattr(self, '_errors'):
            self._errors = []
        self._errors.append(error)



