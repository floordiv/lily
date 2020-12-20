from lily.core.lexer.lexer import Lexer


def parse(raw_json, context=None):
    lexer = Lexer(raw_json, context=context)
    lexemes = lexer.parse()
    # TODO: complete json parser after dictionaries implementation
