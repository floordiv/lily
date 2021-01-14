from itertools import chain
from re import finditer

from core.utils.tokentypes import (NEWLINE, VARIABLE,
                                   MATHEXPR, pytypes2lotus, CLASSINSTANCE,
                                   LIST, DICT, VARASSIGN)

escape_characters = {
    '\\n': '\n',
    '\\r': '\r',
    '\\b': '\b',
    '\\t': '\t',
    '\\a': '\a',
    '\\f': '\f',
    '\\v': '\v',
    # '\\\'': '\'',
    # '\\\"': '\"',
}


def process_escape_characters(raw):
    for raw_character, to_replace in escape_characters.items():
        raw = raw.replace(raw_character, to_replace)

    return raw


def isfloat(string):
    try:
        float(string)

        return True
    except ValueError:
        return False


def parse_func_args(context, args_tokens, basic_token, leave_tokens=True):
    """
    TODO: remove useless args from all the calls
    """

    args = []
    kwargs = {}
    get_value = lambda token_: token_ if leave_tokens else token.value

    for token in args_tokens.value:
        if token.type == VARASSIGN:
            var, val = token.name, token.value

            if val.type == MATHEXPR:
                val = val.value[0]

            kwargs[get_value(var)] = get_value(val)
        else:
            args.append(get_value(token))

    return args, kwargs


def remove_comment(line, comment='#'):
    if line.startswith(comment):
        return ''

    string_pairs = get_string_pairs_indexes(line)

    for comment_index in finditer(comment, line):
        comment_index = comment_index.start()

        if comment_index not in string_pairs:
            return line[:comment_index]

    return line


def get_string_pairs_indexes(line):
    indexes = []
    in_string = False
    prev_string_opener = None

    for index, letter in enumerate(line):
        if letter in ('"', "'"):
            if letter == prev_string_opener:
                in_string = False
            elif not in_string:
                in_string = True
                prev_string_opener = letter

            indexes.append(index)

    if len(indexes) % 2 != 0:
        indexes = indexes[:-1]

    return list(chain.from_iterable([range(*pair) for pair in group_by_pairs(indexes)]))


def group_by_pairs(lst):
    result = []

    for index in range(0, len(lst), 2):
        result.append([lst[index], lst[index + 1]])

    return result


def split_tokens(tokens, splitby=(NEWLINE,), exclude=()):
    if not isinstance(splitby, (list, tuple)):
        splitby = (splitby,)

    split_tokens_result = [[]]

    for token in tokens:
        if not hasattrs(token, ('type', 'primary_type')):   # this is not our token
            split_tokens_result[-1].append(token)
            continue

        if token.type in exclude or token.primary_type in exclude:
            continue

        if token.type in splitby or token.primary_type in splitby:
            split_tokens_result.append([])
            continue

        split_tokens_result[-1].append(token)

    return split_tokens_result


def process_token(token, context):
    if token.type == VARIABLE:
        value = context[token.value]

        if hasattr(value, 'primary_type'):
            value = value.value

        token.type = pytypes2lotus[type(value)]
        token.value = value

    if token.exclam:
        token.value = not token.value
        token.exclam = False

    return token


def get_token_index(list_, token_type):
    for index, token in enumerate(list_):
        if token_type in (token.type, token.primary_type):
            return index

    return None


def readfile(path):
    with open(path) as fd:
        return fd.read()


def contains(source, token_type):
    return bool([token for token in source if token_type in (token.type, token.primary_type)])


def create_token(context, basic_token, class_instance, value, unary='+'):
    if hasattr(value, 'type') and value.type in (LIST, DICT):
        return value

    try:
        token_type = pytypes2lotus[type(value)]
    except KeyError:
        if isinstance(value, class_instance):
            token_type = CLASSINSTANCE
        else:
            return value

    return basic_token(context, token_type, value, unary=unary)


def hasattrs(obj, attrs):
    return all(hasattr(obj, attr) for attr in attrs)


def get_rid_of_tokens(tokens, get_rid_of=NEWLINE):
    if not hasattrs(get_rid_of, '__contains__'):
        get_rid_of = (get_rid_of,)

    output = []

    for token in tokens:
        if token.type in get_rid_of:
            continue

        output.append(token)

    return output
