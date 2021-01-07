from core.utils.tokens import (Function, VarAssign, ForLoop, WhileLoop,
                               IfBranchLeaf, ElifBranchLeaf, ElseBranchLeaf,
                               FunctionCall, BasicToken, ReturnStatement,
                               BreakStatement, ContinueStatement, Branch,
                               ImportStatement, Class)
from core.utils.keywords import (IF_KEYWORD, ELIF_KEYWORD, ELSE_KEYWORD,
                                 FOR_LOOP_KEYWORD, WHILE_LOOP_KEYWORD,
                                 FUNCASSIGN_KEYWORD, RETURN_KEYWORD,
                                 BREAK_KEYWORD, CONTINUE_KEYWORD,
                                 IMPORT_KEYWORD, AS_KEYWORD, CLASSASSIGN_KEYWORD)
from core.utils.tokentypes import (VARIABLE, PARENTHESIS, BRACES,
                                   FBRACES, ANY, NEWLINE,
                                   MATHEXPR, IF_BLOCK, ELIF_BLOCK,
                                   ELSE_BLOCK, STRING, LIST, DICT, TUPLE)
from core.utils.operators import characters
from core.utils.tools import get_token_index
from core.semantic.parsers import (if_elif_branch, else_branch,
                                   function_call, function_assign,
                                   for_loop, while_loop, var_assign,
                                   return_token, break_token, continue_token,
                                   import_statement, class_assign,
                                   parse_list, parse_dict, parse_tuple)


class MatchToken:
    def __init__(self, *match_token_types, primary_types=tuple(), value=None):
        if not isinstance(primary_types, tuple):
            primary_types = (primary_types,)

        self.types = match_token_types
        self.primary_types = primary_types
        self.value = value

    def match(self, another_token):
        if another_token.primary_type in self.primary_types and ANY in self.types:
            return True

        return ANY in self.types or another_token.type in self.types or another_token.value == self.value

    def __str__(self):
        return f'MatchToken(types={self.types}, primary_types={self.primary_types})'


constructions = {
    Function: (
    MatchToken(FUNCASSIGN_KEYWORD), MatchToken(VARIABLE), MatchToken(BRACES, TUPLE, primary_types=(PARENTHESIS, TUPLE)),
    MatchToken(FBRACES, primary_types=PARENTHESIS)),
    Class: (MatchToken(CLASSASSIGN_KEYWORD), MatchToken(VARIABLE), MatchToken(FBRACES, primary_types=PARENTHESIS)),
    VarAssign: (MatchToken(VARIABLE, BRACES, TUPLE), MatchToken(characters['=']), MatchToken(ANY)),
    ForLoop: (MatchToken(FOR_LOOP_KEYWORD), MatchToken(BRACES, primary_types=PARENTHESIS),
              MatchToken(FBRACES, primary_types=PARENTHESIS)),
    WhileLoop: (MatchToken(WHILE_LOOP_KEYWORD), MatchToken(BRACES, primary_types=PARENTHESIS),
                MatchToken(FBRACES, primary_types=PARENTHESIS)),
    IfBranchLeaf: (MatchToken(IF_KEYWORD), MatchToken(BRACES, primary_types=PARENTHESIS),
                   MatchToken(FBRACES, primary_types=PARENTHESIS)),
    ElifBranchLeaf: (
        MatchToken(ELIF_KEYWORD), MatchToken(BRACES, primary_types=PARENTHESIS),
        MatchToken(FBRACES, primary_types=PARENTHESIS)),
    ElseBranchLeaf: (MatchToken(ELSE_KEYWORD), MatchToken(FBRACES, primary_types=PARENTHESIS)),
    FunctionCall: (MatchToken(VARIABLE), MatchToken(BRACES, TUPLE, primary_types=(PARENTHESIS, TUPLE))),
    ReturnStatement: (MatchToken(RETURN_KEYWORD), MatchToken(ANY)),
    BreakStatement: (MatchToken(BREAK_KEYWORD),),
    ContinueStatement: (MatchToken(CONTINUE_KEYWORD),),
    ImportStatement: (MatchToken(IMPORT_KEYWORD), MatchToken(STRING), MatchToken(AS_KEYWORD), MatchToken(VARIABLE)),

}
parsers = {
    Function: function_assign,
    VarAssign: var_assign,
    ForLoop: for_loop,
    WhileLoop: while_loop,
    IfBranchLeaf: if_elif_branch,
    ElifBranchLeaf: if_elif_branch,
    ElseBranchLeaf: else_branch,
    FunctionCall: function_call,
    ReturnStatement: return_token,
    BreakStatement: break_token,
    ContinueStatement: continue_token,
    ImportStatement: import_statement,
    Class: class_assign,
}
token_types_parsers = {
    LIST: parse_list,
    DICT: parse_dict,
    TUPLE: parse_tuple,
}


def match(original, match_list, ignore=()):
    current_match_token_index = 0
    matched = []

    for token in original:
        if token.type in ignore or token.primary_type in ignore:
            continue

        if not match_list[current_match_token_index].match(token):
            return False

        matched.append(token)
        current_match_token_index += 1

    if len(matched) != len(match_list):
        # if output tokens counter does not equals match list length,
        # it means, that match_list does not matches given array
        # of tokens
        return False

    return matched


def startswith(tokens):
    for construction_name, construction_match_tokens in constructions.items():
        match_result = match(tokens[:len(construction_match_tokens)], construction_match_tokens, ignore=(NEWLINE,))

        if match_result:
            if construction_name == VarAssign:
                match_result = tokens[:get_token_index(tokens, NEWLINE)]

            return construction_name, match_result

    return None, None


def branches_leaves_to_branches_trees(executor, evaluator, tokens):
    temp_branch = None
    output_tokens = []

    for token in tokens:
        if token.type in (IF_BLOCK, ELIF_BLOCK, ELSE_BLOCK):
            if temp_branch is None:
                if token.type != IF_BLOCK:
                    raise SyntaxError('Found elif/else statement, but no if statements found')

                temp_branch = Branch(executor, evaluator, token)
            else:
                if temp_branch.type == ELIF_BLOCK:
                    temp_branch.elif_exprs.append(token)
                else:
                    temp_branch.else_expr = token
        elif temp_branch:
            output_tokens.extend((temp_branch, token))
            temp_branch = None
        else:
            output_tokens.append(token)

    if temp_branch:
        output_tokens.append(temp_branch)

    return output_tokens


def parse(context, executor, evaluator, tokens):
    temp = parse_tokens(context, executor, evaluator, tokens=tokens[:])
    temp_math_expr_tokens = []
    output_tokens = []

    while temp:
        construction, tokens = startswith(temp)

        if construction is None:
            value = temp.pop(0)

            if value.type != NEWLINE:
                temp_math_expr_tokens.append(value)
        else:
            if temp_math_expr_tokens:
                token = BasicToken(context, MATHEXPR, temp_math_expr_tokens)
                output_tokens.append(token)
                temp_math_expr_tokens.clear()

            parser = parsers[construction]
            construction_args = parser(executor, evaluator, context, parse, tokens)
            parsed_construction = construction(*construction_args)
            output_tokens.append(parsed_construction)
            temp = temp[len(tokens):]

    if temp_math_expr_tokens:
        token = BasicToken(context, MATHEXPR, temp_math_expr_tokens)
        output_tokens.append(token)

    return branches_leaves_to_branches_trees(executor, evaluator, output_tokens)


def parse_tokens(*args, tokens):
    return list(map(lambda token: parse_token(*args, token), tokens))


def parse_token(context, executor, evaluator, token):
    if token.type in token_types_parsers:
        token_parser = token_types_parsers[token.type]

        return token_parser(executor, evaluator, context, parse, token)

    return token
