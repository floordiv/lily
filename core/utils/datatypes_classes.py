from lily.core.utils.tokentypes import LIST, DICT
from lily.core.utils.tools import create_token


class DefaultBehaviour:
    ...


class List:
    def __init__(self, token):
        self.token = token
        self.type = self.primary_type = LIST
        self.value = token.value
        self.context = token.context

        for key, value in token.as_json().items():
            if hasattr(self, key):
                continue    # instead of re-writing declared attributes above

            setattr(self, key, value)

    def contains(self, value):
        return value in [token.value for token in self.value]

    def get(self, index):
        return self.value[index]

    def add(self, item):
        cloned = self.token.clone()
        cloned.value.append(create_token(self.context, item))
        this_list_copy = List(cloned)

        return this_list_copy

    def append(self, item):
        self.value.append(item)

    def __str__(self):
        return f'[{", ".join(str(token.value) for token in self.value)}]'

    __repr__ = __str__
