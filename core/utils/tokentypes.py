# built-in data types
VARIABLE = 'VARIABLE'
INTEGER = 'INTEGER'
FLOAT = 'FLOAT'
STRING = 'STRING'
LIST = 'LIST'
DICT = 'DICT'
BOOL = 'BOOL'
NULL = 'NULL'

# high-level token types
FCALL = 'FCALL'
BRANCH = 'BRANCH'
IF_BLOCK = 'IF_BLOCK'
ELIF_BLOCK = 'ELIF_BLOCK'
ELSE_BLOCK = 'ELSE_BLOCK'
FOR_LOOP = 'FOR_LOOP'
WHILE_LOOP = 'WHILE_LOOP'
FUNCASSIGN = 'FUNCASSIGN'
VARASSIGN = 'VARASSIGN'
CODE = 'CODE'
RETURN_STATEMENT = 'RETURN_STATEMENT'
BREAK_STATEMENT = 'BREAK_STATEMENT'
CONTINUE_STATEMENT = 'CONTINUE_STATEMENT'

# types for lexer
NO_TYPE = 'NO_TYPE'
OPERATOR = 'OPERATOR'
NEWLINE = 'NEWLINE'
SEMICOLON = 'SEMICOLON'

PARENTHESIS = 'PARENTHESIS'  # used for token primary-type
BRACES = 'BRACES'    # ()
QBRACES = 'QBRACES'  # []
FBRACES = 'FBRACES'  # {}
ANY = 'ANY'
MATHEXPR = 'MATHEXPR'


pytypes2lotus = {
    bool: BOOL,
    int: INTEGER,
    float: FLOAT,
    str: STRING,
    type(None): NULL,
}
