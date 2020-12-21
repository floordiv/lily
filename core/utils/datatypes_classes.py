from lily.core.utils.tokentypes import LIST, DICT, INTEGER
from lily.core.utils.tools import create_token
from lily.core.utils.tokens import BasicToken


class _List:
    def __init__(self, context, value):
        self.type = self.primary_type = LIST
        self.context = context
        self.value = value
        self.length = len(value)

        self.unary = '+'

    def contains(self, value):
        return value in [token.value for token in self.value]

    def get(self, index):
        return self.value[index]

    def add(self, item):
        if not isinstance(item, List):
            raise TypeError('only list can be concatenated to list')

        return _List(self.context, self.value.copy() + item.value)

    def append(self, *items):
        extend_by = []

        for item in items:
            extend_by.append(create_token(self.context, BasicToken, item))

        self.value.extend(extend_by)
        self.length += len(items)

    def extend(self, *items):
        extend_by = []

        for item in items:
            if not hasattr(item, 'type') or item.type not in (LIST,):
                raise TypeError('list can be extended only by list or tuple')

            extend_by.extend(item.value)

        self.value.extend(extend_by)
        self.length += len(items)

    def _2pylist(self):
        return [token.value for token in self.value]

    def __iter__(self):
        for token in self.value:
            yield token

    def __str__(self):
        return f'[{", ".join(repr(token.value) for token in self.value)}]'

    __repr__ = __str__


class List(_List):
    def __init__(self, token):
        super(List, self).__init__(token.context, token.value)

        for key, value in token.as_json().items():
            if hasattr(self, key):
                continue    # instead of re-writing declared attributes above

            setattr(self, key, value)


class _Dict:
    def __init__(self, context, value):
        self.type = self.primary_type = DICT
        self.value = value
        self.context = context

    def contains(self, key):
        return key in self.value

    def get(self, item):
        return self.value[item]

    def items(self):
        final = _List(self.context, [])

        for key, value in self.value.items():
            final.append(_List(self.context, [create_token(self.context, BasicToken, key), create_token(self.context, BasicToken, value)]))

        return final

    def __str__(self):
        return str(self.value)

    __repr__ = __str__


class Dict(_Dict):
    def __init__(self, token):
        super(Dict, self).__init__(token.context, token.value)

        for key, value in token.as_json().items():
            if hasattr(self, key):
                continue    # instead of re-writing declared attributes above

            setattr(self, key, value)


class _Integer:
    def __init__(self, value):
        self.type = self.primary_type = INTEGER
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __le__(self, other):
        return self.value <= other

    def __ge__(self, other):
        return self.value >= other

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __divmod__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __pow__(self, power, modulo=None):
        return self.value ** power

    def __and__(self, other):
        return self.value & other

    def __or__(self, other):
        return self.value | other

    def __rshift__(self, other):
        return self.value >> other

    def __lshift__(self, other):
        return self.value << other

    def __bool__(self):
        return bool(self.value)

    def __str__(self):
        return 'str(self.value)'

    __repr__ = __str__


class Integer(_Integer):
    def __init__(self, token):
        if not isinstance(token.value, int):
            token.value = int(token.value)

        super(Integer, self).__init__(token.value)

        for key, value in token.as_json().items():
            if hasattr(self, key):
                continue    # instead of re-writing declared attributes above

            setattr(self, key, value)
