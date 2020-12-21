from lily.core.utils.tools import split_tokens, contains
from lily.core.utils.tokentypes import (COMMA, COLON, LIST,
                                        DICT, QBRACES, FBRACES,
                                        PARENTHESIS, NEWLINE)


"""
this is a raw step. We just say, that this token is a list/dict/tuple/etc..
After lexical analyze (this module used by lexer), comes semantic
It iterates over the values, and parse them. That's all

Actually, I'm trying to implement data types for the 5th time. I hope, it'll work
"""


def parse_list(token):
    token.type = token.primary_type = LIST
    split_by_comma = split_tokens(token.value, COMMA)

    if not (len(split_by_comma) == 1 and split_by_comma[0] == []):
        token.value = split_by_comma

    return token


def parse_dict(token):
    token.type = token.primary_type = DICT
    key_value_pairs = split_tokens(token.value, COMMA, exclude=(NEWLINE,))
    raw_result = {}

    for key, _, value in key_value_pairs:
        raw_result[key] = value

    token.value = raw_result

    return token


token_types_parsers = {
    parse_list: (QBRACES, PARENTHESIS, lambda token: True),
    parse_dict: (FBRACES, PARENTHESIS, lambda token: contains(token.value, COLON)),  # shit code, rewrite it later
}


def process_tokens(tokens):
    return map(process_token, tokens)


def process_token(token):
    if token.primary_type == PARENTHESIS:
        result = list(process_tokens(token.value))
        token.value = result

    for parser, (type_, primary_type, filter_) in token_types_parsers.items():
        if token.type == type_ and token.primary_type == primary_type and filter_(token):
            return parser(token)

    return token
