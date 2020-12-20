from lily.core.utils.tokentypes import LIST, DICT
from lily.core.utils.tools import create_token


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
        if not isinstance(item, List):
            raise TypeError('only list can be concatenated to list')

        cloned = self.token.clone()
        cloned.value.extend(item.value)
        this_list_copy = List(cloned)

        return this_list_copy

    def append(self, *items):
        extend_by = []

        for item in items:
            extend_by.append(create_token(self.context, item))

        self.value.extend(extend_by)

    def extend(self, *items):
        extend_by = []

        for item in items:
            if not hasattr(item, 'type') or item.type not in (LIST,):
                raise TypeError('list can be extended only by list or tuple')

            extend_by.extend(item.value)

        self.value.extend(extend_by)

    def __str__(self):
        return f'[{", ".join(str(token.value) for token in self.value)}]'

    __repr__ = __str__
