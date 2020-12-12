from lily.core.utils.operators import executors
from lily.core.utils.tokens import BasicToken
from lily.core.utils.tokentypes import (OPERATOR, FCALL,
                                        PARENTHESIS, VARIABLE,
                                        NO_TYPE, pytypes2lotus)


def evaluate(tokens, context: dict = None, return_token=False):
    if context is None:
        context = {}

    stack = tokens[:]

    while len(stack) > 1 or (stack and stack[0].primary_type in (PARENTHESIS, FCALL, VARIABLE)):
        op, op_start, op_end = get_op(stack)

        if hasattr(op, 'primary_type') and op.primary_type == PARENTHESIS:
            result = evaluate(op.value, context=context, return_token=True)
            apply_token_unary(result, op.unary)
        else:
            result = evaluate_op(op, context)
            apply_token_unary(result)

        stack[op_start:op_end] = [result]

    if return_token:
        return stack[0]

    return stack[0].value


def get_op(tokens):
    op, op_index = tokens[:3], 0

    if len(op) == 1:    # it potentially can be 2, but fuuck...
        if op[0].primary_type == PARENTHESIS:
            op = op[0]

        return op, 0, 1

    for index, token in enumerate(tokens):
        if token.primary_type in (FCALL, PARENTHESIS):
            return token, index, index + 1

        if token.primary_type == OPERATOR and token.priority > op[1].priority:
            op, op_index = tokens[index-1 if index > 0 else 0:index+2], index

    return op, op_index - 1 if op_index > 0 else 0, op_index + 3


def evaluate_op(op, context):
    if hasattr(op[0], 'type') and op[0].type == FCALL:
        function_response = op[0].execute()
        response_token = BasicToken(context, pytypes2lotus[type(function_response)], function_response, unary=op[0].unary)

        return response_token
    elif len(op) == 1:
        return process_token(op[0], context)

    left, op, right = op
    left, right = process_token(left, context), process_token(right, context)

    if isinstance(left, BasicToken):
        left = left.value
    if isinstance(right, BasicToken):
        right = right.value

    executor = executors[op.value]
    result = executor(left, right)
    result_token = BasicToken(context, pytypes2lotus[type(result)], result)

    return result_token


def process_token(token, context):
    if token.type == VARIABLE:
        value = context[token.value]

        if isinstance(value, BasicToken):
            process_token_exclam(value)
            value = value.value
        else:
            value = BasicToken(context, pytypes2lotus[type(value)], value)
            value.exclam = token.exclam
            process_token_exclam(value)
            apply_token_unary(value, to_unary=token.unary)

        return value

    process_token_exclam(token)

    return token


def process_token_exclam(token):
    if token.exclam:
        token.value = not token.value
        token.exclam = False


def apply_token_unary(token, to_unary=None):
    if to_unary is None:
        to_unary = token.unary

    token.value = -token.value if to_unary == '-' else token.value

    return token
