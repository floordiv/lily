class Context:
    def __init__(self, init_vars=None):
        if init_vars is None:
            init_vars = {}

        self.variables = init_vars

    def __getitem__(self, item):
        return self.variables[item]

    def __setitem__(self, key, value):
        self.variables[key] = value

    def get(self, key, value_instead=None):
        return self.variables.get(key, value_instead)

    def items(self):
        return self.variables.items()

    def __str__(self):
        return f'Context({self.variables})'

    __repr__ = __str__


main_context = Context()
