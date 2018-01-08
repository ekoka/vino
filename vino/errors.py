class VinoError(Exception): pass

class ValidationError(Exception):
    interrupt_validation = False
    def __init__(self, *a, **kw):
        # interrupt_validation is a keyword-only arg
        self.interrupt_validation = kw.pop('interrupt_validation', False)
        super(ValidationError, self).__init__(*a)

class ValidationErrorStack(ValidationError):

    @property
    def errors(self):
        if not hasattr(self, '_errors'):
            self._errors = []
        return self._errors

    @property
    def empty(self):
        return not self.errors

    def clear(self):
        del self.errors[:]

    def pop(self):
        self.errors.pop()

    def append(self, error):
        self.errors.append(error)
        return self

    def __len__(self):
        return len(self.errors)

    def __getitem__(self, item):
        return self.errors[item]




