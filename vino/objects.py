class ObjectSchema:
    def define(self, *processors):
        for p in processors:
            """ if a processor has a `vino_init()` method it will be called.
            It allows to pass a construct to vino that may have to return some
            other object as processor. This is how the native `BooleanProcessor`
            work when not instantiated. When working with a `vino.mandatory`
            processor its construction is simply delayed and a call to `init is
            made here.
            """
            if hasattr(c, 'vino_init'):
                c.vino_init()

