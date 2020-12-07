from sys import exit
from os import listdir

from lily.core.lexer.lexer import Lexer
from lily.core.semantic import semantic
from lily.lib.std.bindings import pybindings
from lily.core.interpreter.eval import evaluate
from lily.core.utils.contexts import main_context, Context
from lily.core.utils.tools import process_escape_characters
from lily.core.utils.tokentypes import (MATHEXPR, RETURN_STATEMENT,
                                        CONTINUE_STATEMENT, BREAK_STATEMENT)


EXECUTOR_GIVE_HANDLING_BACK_IF_TYPES = (CONTINUE_STATEMENT, RETURN_STATEMENT, BREAK_STATEMENT)


def interpret(raw: str, exit_after_execution=True):
    lexer = Lexer(process_escape_characters(raw))
    lexemes = lexer.parse()

    main_context.variables = pybindings  # initialize global namespace
    final_tokens = semantic.parse(main_context, executor, evaluate, lexemes)

    exit_code = executor(final_tokens, context=main_context)

    if exit_code is not None and exit_code.type == RETURN_STATEMENT:
        exit_code = exit_code.value

    if exit_after_execution:
        exit(exit_code or 0)

    return exit_code or 0


def executor(tokens, context=None):
    """
    tokens: tokens after semantic parse
    """

    for token in tokens:
        if token.type == MATHEXPR:
            evaluate(token.clone().value, context=context)
        elif token.type in EXECUTOR_GIVE_HANDLING_BACK_IF_TYPES:
            if token.type == RETURN_STATEMENT:
                token.execute_value()

            return token
        else:
            result = token.execute()

            if hasattr(result, 'type') and result.type in EXECUTOR_GIVE_HANDLING_BACK_IF_TYPES:
                return result


def load_example(name):
    with open('../../examples/' + name + '.lt') as example:
        return example.read()


def test_all(examples_dir='../../examples/', exclude=None):
    if exclude is None:
        exclude = ()

    examples = listdir(examples_dir)
    splitline = '-' * 30

    for example in examples:
        if example in exclude:
            print(splitline)
            print(example + ': skipped')
            continue

        print(splitline)

        with open(examples_dir + example) as example_fd:
            response = interpret(example_fd.read(), exit_after_execution=False)
            print(example, f'(exit-code: {response})')

    print(splitline)


interpret(load_example('simple_program_demo'))
# test_all(exclude=['simple_program_demo.lt'])
# interpret('print(-!false)')
