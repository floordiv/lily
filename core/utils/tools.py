from itertools import chain
from re import finditer

from lily.core.utils.tokentypes import (NEWLINE, VARIABLE,
                                        MATHEXPR, pytypes2lotus)
from lily.core.utils.operators import characters
from lily.core.utils.tokens import BasicToken


escape_characters = {
    '\\n': '\n',
    '\\r': '\r',
    '\\b': '\b',
    '\\t': '\t',
    '\\a': '\a',
    '\\f': '\f',
    '\\v': '\v',
    '\\\'': '\'',
    '\\\"': '\"'
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


def parse_func_args(context, args_tokens, leave_tokens=True):
    args = []
    kwargs = {}
    get_value = lambda token: token if leave_tokens else token.value

    for tokens in split_tokens(args_tokens.value, 'COMMA'):
        if len(tokens) == 3 and tokens[1].type == characters['=']:
            var, _, val = tokens
            kwargs[var.value] = get_value(val)
        elif len(tokens) == 1:
            args.append(get_value(tokens[0]))
        else:
            args.append(BasicToken(context, MATHEXPR, tokens))

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


def split_tokens(tokens, splitby=(NEWLINE,)):
    split_tokens_result = [[]]

    for token in tokens:
        if token.type in splitby or token.primary_type and token.primary_type in splitby:
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
