from lily.lib.std.bindings import pybindings
from lily.core.utils.tokentypes import LIST, DICT


class Context:
    def __init__(self, init_vars=None):
        if init_vars is None:
            init_vars = pybindings.copy()

        self.variables = init_vars

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        *split_key, last_var = key.split('.')

        if split_key and split_key[0] == 'global':
            split_key = split_key[1:]
            variables = main_context.variables
        else:
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

    def get(self, key):
        first_varpath_element, *varpath = key.split('.')

        if first_varpath_element not in self.variables:
            variables = main_context.variables
        elif first_varpath_element == 'global':
            variables = main_context.variables
            first_varpath_element, *varpath = varpath
        else:
            variables = self.variables

        value = variables[first_varpath_element]

        for var in varpath:
            if hasattr(value, 'type') and value.type not in (LIST, DICT):
                value = value.context
            elif hasattr(value, '__dict__') and not isinstance(value, Context):    # to support python calls
                value = Context(init_vars={var: getattr(value, var) for var in dir(value)})

            value = value[var]

        return value

    def items(self):
        return self.variables.items()

    def copy(self):
        return Context(init_vars=self.variables.copy())

    def __instancecheck__(self, instance):
        """
        isinstance(ParentContext, ChildrenContext) - shows whether ParentContext contains ChildrenContext
        """

        for value in self.variables.values():
            if instance is value:
                return True

        return False

    def __str__(self):
        return f'Context({self.variables})'

    __repr__ = __str__


main_context = Context()
