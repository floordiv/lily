from lily.core.utils.tokentypes import LIST, DICT, TUPLE
from lily.core.utils.tools import create_token
from lily.core.utils.tokens import BasicToken, ClassInstance


def apply_token_attrs(self, token):
    for key, value in token.as_json().items():
        if hasattr(self, key):
            continue  # instead of re-writing declared attributes above

        setattr(self, key, value)


class _List:
    def __init__(self, evaluator, context, value):
        self.evaluator = evaluator
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
        if not isinstance(item, list):
            raise TypeError('only list can be concatenated to list')

        return _List(self.evaluator, self.context, self.value.copy() + item)

    def append(self, *items):
        extend_by = []

        for item in items:
            extend_by.append(create_token(self.context, BasicToken, ClassInstance, item))

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

    def execute(self, context):
        for value in self.value:
            print(value, '<- what the fuck in list?')

        self.value = [self.evaluator(value, context) for value in self.value]

    def __add__(self, other):
        return self.add(other)

    def __iter__(self):
        for token in self.value:
            yield token

    def __str__(self):
        return f'[{", ".join(repr(token.value) for token in self.value)}]'

    __repr__ = __str__


class List(_List):
    def __init__(self, evaluator, token):
        super(List, self).__init__(evaluator, token.context, token.value)
        apply_token_attrs(self, token)


class _Tuple:
    def __init__(self, evaluator, value):
        self.evaluator = evaluator
        self.type = self.primary_type = TUPLE
        self.value = tuple(value)
        self.length = len(value)

    def get(self, index):
        return self.value[index]

    def execute(self, context):
        for value in self.value:
            print(value, '<- what the fuck in tuple?')

        self.value = (self.evaluator(value, context) for value in self.value)

    def __iter__(self):
        for token in self.value:
            yield token

    def __str__(self):
        return f'({", ".join(repr(token.value) for token in self.value)})'

    __repr__ = __str__


class Tuple(_Tuple):
    def __init__(self, evaluator, token):
        super(Tuple, self).__init__(evaluator, token.value)
        apply_token_attrs(self, token)


class _Dict:
    def __init__(self, evaluator, context, value):
        self.evaluator = evaluator
        self.type = self.primary_type = DICT
        self.value = value
        self.context = context

    def contains(self, key):
        return key in self.value

    def get(self, item):
        return self.value[item]

    def items(self):
        final = _List(self.evaluator, self.context, [])

        for key, value in self.value.items():
            final.append(_List(self.evaluator, self.context,
                               [create_token(self.context, BasicToken, ClassInstance, key),
                                create_token(self.context, BasicToken, ClassInstance, value)]))

        return final

    def execute(self, context):
        for value in self.value:
            print(value, '<- what the fuck in dict?')

        self.value = {key: self.evaluator(value, context) for key, value in self.value.items()}

    def __str__(self):
        return str(self.value)

    __repr__ = __str__


class Dict(_Dict):
    def __init__(self, evaluator, token):
        super(Dict, self).__init__(evaluator, token.context, token.value)
        apply_token_attrs(self, token)
