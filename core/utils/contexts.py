from lily.lib.std.bindings import pybindings


class Context:
    def __init__(self, init_vars=None):
        if init_vars is None:
            init_vars = pybindings.copy()

        self.variables = init_vars

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        *split_key, last_var = key.split('.')
        variables = self.variables

        for key_element in split_key:
            if key_element not in variables:
                variables[key_element] = Context()
            elif hasattr(variables, 'type'):    # this is some kinda token
                variables = variables.context

            variables = variables[key_element]

        if hasattr(variables, 'type'):
            variables = variables.context

        variables[last_var] = value

    def get(self, key, value_instead=None):
        first_varpath_element, *varpath = key.split('.')
        value = self.variables[first_varpath_element]

        try:
            for var in varpath:
                if hasattr(value, 'type'):
                    value = value.context

                value = value.get(var)
        except AttributeError:
            return value_instead

        return value

    def items(self):
        return self.variables.items()

    def __str__(self):
        return f'Context({self.variables})'

    __repr__ = __str__


main_context = Context()
