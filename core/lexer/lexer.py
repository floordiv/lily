from lily.core.utils import (keywords, tokentypes,
                             operators, tokens,
                             tools, priorities)


braces_openers = {
    '(': ')',
    '[': ']',
    '{': '}',
}
braces_types = {
    ')': tokentypes.BRACES,
    ']': tokentypes.QBRACES,
    '}': tokentypes.FBRACES,
}


class Lexer:
    def __init__(self, raw=None, context=None):
        if context is None:
            context = {}

        self.raw = raw
        self.context = context

    def prepare_raw_source(self, source):
        prepared_raw = ''

        for line in source.splitlines():
            prepared_line = tools.remove_comment(line).rstrip()
            prepared_raw += prepared_line + '\n'

        return prepared_raw[:-1]

    def parse(self, code=None, context=None):
        if code is None:
            if self.raw is None:
                raise TypeError('no source to lex given')

            code = self.raw
        if context is None:
            context = self.context

        code = self.prepare_raw_source(code)

        output_tokens = [tokens.BasicToken(context, tokentypes.NO_TYPE, '')]
        skip_iters = 0
        dot = operators.characters['.']

        for index, letter in enumerate(code):
            if skip_iters:
                skip_iters -= 1
                continue

            if letter == '\n':
                self.append(output_tokens, tokens.BasicToken(context, tokentypes.NEWLINE, '\n'))
                output_tokens.append(tokens.BasicToken(context, tokentypes.NO_TYPE, ''))
            elif letter == ' ':
                if output_tokens[-1].value in keywords.keywords:    # other way, just skip it
                    keyword = output_tokens[-1].value
                    keyword_type = keywords.keywords[keyword]

                    output_tokens[-1] = tokens.BasicToken(context, keyword_type, keyword)

                self.append(output_tokens, tokens.BasicToken(context, tokentypes.NO_TYPE, ''))
                continue
            elif letter in operators.special_characters:
                if output_tokens[-1].type == tokentypes.OPERATOR and output_tokens[-1].value + letter in operators.characters:
                    output_tokens[-1].value += letter
                else:
                    if letter == '.':
                        output_tokens[-1].value += '.'
                        continue

                    self.append(output_tokens, tokens.BasicToken(context, tokentypes.OPERATOR, letter, primary_type=tokentypes.OPERATOR))
            else:
                if letter in tuple('\'"'):
                    string, skip_iters = self.get_string_ending(code[index:])
                    string_token = tokens.BasicToken(context, tokentypes.STRING, string[1:-1])
                    self.append(output_tokens, string_token)
                    continue

                if output_tokens[-1].type == tokentypes.OPERATOR:
                    self.append(output_tokens, tokens.BasicToken(context, tokentypes.NO_TYPE, ''))

                output_tokens[-1].value += letter

        self.provide_token_type(output_tokens[-1])
        parsed_but_no_unary = self.parse_braces(context, output_tokens)

        final = self.parse_unary(parsed_but_no_unary)

        if final[-1].value == '':
            final.pop()

        return final

    def append(self, lst: list, item: any):
        if lst[-1].type == tokentypes.NO_TYPE and lst[-1].value == '':
            lst[-1] = item
        else:
            lst.append(item)

        if len(lst) > 1:
            self.provide_token_type(lst[-2])

    def get_string_ending(self, string):
        opener = string[0]

        for index, letter in enumerate(string[1:], start=1):
            if letter == opener and string[index - 1] != '\\':
                return string[:index + 1], index

        return string, -1

    def provide_token_type(self, token):
        if token.value.isdigit():
            token.type = token.primary_type = tokentypes.INTEGER
            token.value = int(token.value)
        elif tools.isfloat(token.value):
            token.type = token.primary_type = tokentypes.FLOAT
            token.value = float(token.value)
        elif token.type == tokentypes.NO_TYPE:
            token.type = token.primary_type = tokentypes.VARIABLE
        elif token.primary_type == tokentypes.OPERATOR:
            if token.value in priorities.for_tokens:
                token.priority = priorities.for_tokens[token.value]

            token.type = operators.characters[token.value]

    def parse_unary(self, tokens_):
        output_tokens = []
        temp_signs = []

        for token in tokens_:
            if token.primary_type == tokentypes.PARENTHESIS:
                token.value = self.parse_unary(token.value)

            if token.primary_type == tokentypes.OPERATOR and (not output_tokens or output_tokens[-1].primary_type == tokentypes.OPERATOR):
                temp_signs.append(token)
            else:
                if temp_signs:
                    output_tokens.append(self.get_unary_token(token, temp_signs))
                    temp_signs.clear()
                    continue

                output_tokens.append(token)

        return output_tokens

    def get_unary_token(self, token, signs):
        reversed_signs = signs[::-1]
        final_sign = reversed_signs[0].value
        final_token_exclam = token.exclam

        if final_sign == '!':
            final_token_exclam = not final_token_exclam

        for sign in reversed_signs[1:]:
            if sign.value == '-' and final_sign == '-':
                final_sign = '+'
            elif sign.value == '+' and final_sign == '-':
                final_sign = '-'
            elif sign.value == '!':
                final_token_exclam = not final_token_exclam
            else:
                final_sign = sign.value

        token.unary = final_sign
        token.exclam = final_token_exclam

        if token.type in (tokentypes.INTEGER, tokentypes.FLOAT):
            self.apply_unary(token)

            if token.exclam:
                token.type = token.primary_type = tokentypes.BOOL

        return token

    def apply_unary(self, token):
        if token.unary == '-':
            token.value = -token.value

        if token.exclam:
            token.value = not token.value

    def parse_braces(self, context, tokens_):
        opener = None
        opened = 0
        temp = []
        output = []

        for token in tokens_:
            if token.value in braces_openers:
                if opener is None:
                    opener = token.value
                elif token.value == opener:
                    opened += 1
                    temp.append(token)
                else:
                    temp.append(token)
            elif opener and token.value == braces_openers[opener]:
                if opened:
                    opened -= 1
                    temp.append(token)
                else:
                    braces_type = braces_types[token.value]
                    new_token = tokens.BasicToken(context, braces_type, self.parse_braces(context, temp),
                                                  primary_type=tokentypes.PARENTHESIS)

                    output.append(new_token)

                    temp.clear()
                    opener = None
                    opened = 0
            elif opener is not None:
                temp.append(token)
            else:
                output.append(token)

        if temp:
            raise SyntaxError('unclosed braces')

        return output


# lexer = Lexer("class FirstClass.MyClass { func hello_world() { print('hello, world!') } }")
# lexemes = lexer.parse()
# print(lexemes)
