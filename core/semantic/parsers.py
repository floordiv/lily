from core.utils.tokens import BasicToken
from core.utils.datatypes_classes import List, Dict, Tuple
from core.utils.tools import parse_func_args, split_tokens, process_token
from core.utils.tokentypes import (SEMICOLON, MATHEXPR, PARENTHESIS,
                                   LIST, DICT, NEWLINE)

TOKEN_TYPES_FOR_SEMANTIC_ANALYZE = (MATHEXPR, LIST, DICT)


def function_call(executor, evaluator, context, semantic_parser, tokens):
    name, args_kwargs = tokens

    if args_kwargs.primary_type == PARENTHESIS:
        # not a tuple, but single-value braces
        args, kwargs = semantic_parser(context, executor, evaluator, args_kwargs.value), {}
    else:
        args, kwargs = parse_func_args(context, args_kwargs, BasicToken, leave_tokens=True)

    args = _parse_args(context, executor, evaluator, args, semantic_parser)

    return evaluator, name.value, args, kwargs, name.unary, name.exclam


def function_assign(executor, evaluator, context, semantic_parser, tokens):
    _, name, args_kwargs, code = tokens
    args, kwargs = parse_func_args(context, args_kwargs, BasicToken, leave_tokens=True)

    if args and args[0].type == MATHEXPR:
        args = []

    return executor, name.value, args, kwargs, semantic_parser(context, executor, evaluator, code.value)


def class_assign(executor, evaluator, context, semantic_parser, tokens):
    _, name, body = tokens

    return context, executor, name.value, semantic_parser(context, executor, evaluator, body.value)


def if_elif_branch(executor, evaluator, context, semantic_parser, tokens):
    _, expr, code = tokens

    return expr.value, semantic_parser(context, executor, evaluator, code.value)


def else_branch(executor, evaluator, context, semantic_parser, tokens):
    _, code = tokens

    return (semantic_parser(context, executor, evaluator, code.value),)


def for_loop(executor, evaluator, context, semantic_parser, tokens):
    _, start_end_step, code = tokens
    start, end, step = map(lambda item: semantic_parser(context, executor, evaluator, item),
                           split_tokens(start_end_step.value, (SEMICOLON,)))
    start, step = start[0], step[0]

    return executor, evaluator, start, end, step, semantic_parser(context, executor, evaluator, code.value)


def while_loop(executor, evaluator, context, semantic_parser, tokens):
    _, expr, code = tokens

    return executor, evaluator, expr.value, semantic_parser(context, executor, evaluator, code.value)


def var_assign(executor, evaluator, context, semantic_parser, tokens):
    name, _, *value = tokens
    value = semantic_parser(context, executor, evaluator, value)

    return evaluator, name, value[0]


def execute_code(executor, evaluator, context, semantic_parser, tokens):
    _, *code = tokens
    code = semantic_parser(context, executor, evaluator, code)[0]

    if code.type == MATHEXPR:
        code = code.value[0]

    return executor, lambda _tokens: semantic_parser(context, executor, evaluator, _tokens), code


def evaluate_code(executor, evaluator, context, semantic_parser, tokens):
    _, *code = tokens
    code = semantic_parser(context, executor, evaluator, code)[0]

    if code.type == MATHEXPR:
        code = code.value[0]

    return evaluator, lambda _tokens: semantic_parser(context, executor, evaluator, _tokens), code


def return_token(executor, evaluator, context, semantic_parser, tokens):
    _, *value = tokens
    value = semantic_parser(context, executor, evaluator, value)[0]

    if value.primary_type == PARENTHESIS:
        value = _parse_args(context, executor, evaluator, value.value, semantic_parser)
    else:
        value = [process_token(value, context)]

    return evaluator, value


def break_token(executor, evaluator, context, semantic_parser, tokens):
    return tuple()


def continue_token(executor, evaluator, context, semantic_parser, tokens):
    return tuple()


def import_statement(executor, evaluator, context, semantic_parser, tokens):
    _, path, _, name = tokens

    return path.value, name.value


def pyimport_statement(executor, evaluator, context, semantic_parser, tokens):
    _, path, _, name = tokens

    return path.value, name.value


def try_except_block(executor, evaluator, context, semantic_parser, tokens):
    try_keyword, code, _, errhandler = tokens
    code = semantic_parser(context, executor, evaluator, code.value)
    errhandler = semantic_parser(context, executor, evaluator, errhandler.value)

    return executor, code, errhandler


def _parse_args(context, executor, evaluator, args, parse_semantic):
    output = []

    for arg in args:
        if arg.type in TOKEN_TYPES_FOR_SEMANTIC_ANALYZE:
            if len(arg.value) == 0:
                continue

            arg = parse_semantic(context, executor, evaluator, arg.value if arg.type == MATHEXPR else [arg])[0]

        output.append(arg)

    return output


# data types parsers

def parse_list(executor, evaluator, context, semantic_parser, token):
    if isinstance(token, List):  # already parsed
        return token

    for index, value in enumerate(token.value):
        parsed_value = semantic_parser(context, executor, evaluator, value)

        if not parsed_value:
            del token.value[index]
            continue

        parsed_value = parsed_value[0]

        if parsed_value.type == MATHEXPR:
            parsed_value = parsed_value.value[0]

        token.value[index] = parsed_value

    return List(evaluator, token)


def parse_tuple(executor, evaluator, context, semantic_parser, token):
    if isinstance(token, Tuple):
        return token

    for index, value in enumerate(token.value):
        if not value:
            del token.value[index]
            continue

        parsed_value = semantic_parser(context, executor, evaluator, value)[0]

        if parsed_value.type == MATHEXPR:
            mathexpr_value = parsed_value.value

            if len(mathexpr_value) == 1:
                parsed_value = mathexpr_value[0]
            else:
                parsed_value = semantic_parser(context, executor, evaluator, parsed_value.value)[0]

        token.value[index] = parsed_value

    return Tuple(evaluator, token)


def parse_dict(executor, evaluator, context, semantic_parser, token):
    if isinstance(token, Dict):
        return token  # dict already parsed

    cooked_dict = {}

    for key, value in token.value.items():
        parsed_value = semantic_parser(context, executor, evaluator, [value])[0]

        if parsed_value.type == MATHEXPR:
            parsed_value = parsed_value.value[0]

        key, value = evaluator([key], context=context), evaluator([parsed_value], context=context)
        cooked_dict[key] = value

    token.value = cooked_dict

    return Dict(evaluator, token)
