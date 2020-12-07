from math import pi

from lily.core.lexer.lexer import Lexer
from lily.core.interpreter.eval import evaluate


exprs = (
    "2+2*2",
    "(2+2)+(2+2)",
    "-(2+2)+-(2+2)",
    "(2+2)*-(2+2)",
    "-(-(-(-(3*88888))))",
    "pi*2",
    "(pi+1)*(pi+2)",
    "-pi",
    "pi**2",
    '1+(1+1)',
    '(1+1)+1',
    '(1+1)+(1+1)',
    '-(1+1)+(1+1)',
    '+-(1+1)+(1+1)',
    '-+(1+1)+(1+1)',
    '(-5)',
    '-(1+x)',
    '---1',
)

x = 5
lexer = Lexer()

for expr in exprs:
    print(expr, end=' ')
    lexemes = lexer.parse(expr)
    evaluated = evaluate(lexemes, context={'pi': pi, 'x': x})
    should_be = eval(expr)
    print('=', evaluated, 'passed' if evaluated == should_be else f'failed (should be: {should_be})')
# print(evaluate(lexer.parse("user_input == 'quit' || user_input == 'exit'"), context={'user_input': 'no'}))
