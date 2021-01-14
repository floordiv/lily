from core.utils.tools import create_token
from core.utils.operators import executors
from core.utils.tokens import BasicToken, ClassInstance
from core.utils.tokentypes import (OPERATOR, FCALL,
                                   PARENTHESIS, VARIABLE,
                                   pytypes2lotus, CLASSINSTANCE,
                                   LIST, DICT, TUPLE, MATHEXPR)


def evaluate(tokens, context: dict = None, return_token=False):
    if context is None:
        context = {}

    stack = tokens[:]

    if not all(hasattr(stack[0], attr) for attr in ('type', 'primary_type')):
        return stack[0]  # this is not our token

    for index, token in enumerate(stack):
        if token.type == MATHEXPR:
            stack[index] = evaluate(token.value, context=context, return_token=True)

    while len(stack) > 1 or (stack and stack[0].primary_type in (PARENTHESIS, FCALL, VARIABLE)):
        op, op_start, op_end = get_op(stack)

        if hasattr(op, 'primary_type') and op.primary_type == PARENTHESIS:
            result = evaluate(op.value, context=context, return_token=True)
            process_token_exclam(result, op)
            apply_token_unary(result, op.unary)
        else:
            result = evaluate_op(op, context)
            apply_token_unary(result)

        stack[op_start:op_end] = [result]

    unpack_stack = stack[0]

    if return_token or unpack_stack.type in (LIST, DICT, TUPLE):
        return unpack_stack

    return unpack_stack.value


def get_op(tokens):
    op, op_index = tokens[:3], 0

    if len(op) == 1:  # it potentially can be 2, but fuuck...
        if op[0].primary_type == PARENTHESIS:
            op = op[0]

        return op, 0, 1

    for index, token in enumerate(tokens):
        if token.primary_type in (FCALL, PARENTHESIS):
            return token, index, index + 1

        if token.primary_type == OPERATOR and token.priority > op[1].priority:
            op, op_index = tokens[index - 1 if index > 0 else 0:index + 2], index

    return op, op_index - 1 if op_index > 0 else 0, op_index + 3


def evaluate_op(op, context):
    if not isinstance(op, list):
        op = [op]

    if hasattr(op[0], 'type') and op[0].type == FCALL:
        func = op[0]
        function_response = func.execute(context)

        return create_token(context, BasicToken, ClassInstance, function_response, unary=op[0].unary)
    elif len(op) == 1:
        return process_token(op[0], context)

    left, op, right = op
    left = process_token(left, context).value
    right = process_token(right, context).value
    executor = executors[op.value]
    result = executor(left, right)

    return create_token(context, BasicToken, ClassInstance, result)


def process_token(token, context):
    if token.type == VARIABLE:
        value = context[token.value]

        if isinstance(value, BasicToken):
            process_token_exclam(value)
        else:
            value = BasicToken(context, pytypes2lotus.get(type(value), CLASSINSTANCE), value)
            value.exclam = token.exclam
            process_token_exclam(value)
            apply_token_unary(value, to_unary=token.unary)

        return value

    process_token_exclam(token)

    return token


def process_token_exclam(token, of_token=None):
    if of_token is None:
        of_token = token

    if of_token.exclam:
        token.value = not token.value
        token.exclam = False


def apply_token_unary(token, to_unary=None):
    if to_unary is None:
        to_unary = token.unary

    token.value = -token.value if to_unary == '-' else token.value

    return token
