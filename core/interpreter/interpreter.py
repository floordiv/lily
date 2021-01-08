from json import load
from os import chdir, path as os_path
from sys import exit, path as sys_path

from core.lexer.lexer import Lexer
from core.semantic import semantic
from core.interpreter.eval import evaluate
from core.utils.contexts import main_context, Context
from core.utils.tools import process_escape_characters
from core.utils.tokentypes import (MATHEXPR, RETURN_STATEMENT,
                                   CONTINUE_STATEMENT, BREAK_STATEMENT,
                                   IMPORT_STATEMENT)

EXECUTOR_GIVE_HANDLING_BACK_IF_TYPES = (CONTINUE_STATEMENT, RETURN_STATEMENT, BREAK_STATEMENT)


def interpret(raw: str, context=None, exit_after_execution=True):
    if context is None:
        main_context.clear()
        context = main_context

    lexer = Lexer(process_escape_characters(raw))
    lexemes = lexer.parse()
    final_tokens = semantic.parse(context, executor, evaluate, lexemes)
    exit_code = executor(final_tokens, context=context)

    if exit_code is not None and exit_code.type == RETURN_STATEMENT:
        exit_code = exit_code.value

    if exit_after_execution:
        exit(exit_code or 0)

    return exit_code or 0


def executor(tokens, context=None):
    """
    tokens: tokens after semantic parse
    """

    if context is None:
        context = Context()
    if isinstance(tokens, str):  # this is raw
        return interpret(tokens, context=context, exit_after_execution=False)

    for token in tokens:
        if token.type == IMPORT_STATEMENT:
            interpreted, module_context = import_file(token.path)
            context[token.name] = module_context
        elif token.type == MATHEXPR:
            evaluate(token.clone().value, context=context)
        elif token.type in EXECUTOR_GIVE_HANDLING_BACK_IF_TYPES:
            if token.type == RETURN_STATEMENT:
                token.execute_value(context)

            return token
        else:
            result = token.execute(context)

            if hasattr(result, 'type') and result.type in EXECUTOR_GIVE_HANDLING_BACK_IF_TYPES:
                return result


def import_file(path):
    with open('./' + path) as fd:
        source = fd.read()

    new_context = Context()

    return interpret(source, context=new_context, exit_after_execution=False), new_context
