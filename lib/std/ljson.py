from core.lexer.lexer import Lexer
from core.utils.tools import get_rid_of_tokens
from core.utils.tokentypes import DICT, LIST, NEWLINE, VARIABLE


class JsonParser:
    def __init__(self, json):
        self.json = json

    def parse(self, json=None):
        if json is None:
            json = self.json

        lexer = Lexer(json)
        lexemes = get_rid_of_tokens(lexer.parse(), NEWLINE)
        output = [self.process_element(elem) for elem in lexemes]

        if len(lexemes) == 1:   # default json
            output = output[0]

        return output

    def process_element(self, element, return_on_err=None):
        if element.type == LIST:
            return self.process_list(element)
        elif element.type == DICT:
            return self.process_dict(element)
        elif element.type == VARIABLE:
            if element.value == 'null':
                return None

            if element.value not in ('true', 'false'):
                raise TypeError('unknown variable: ' + element.value)

            return element.value == 'true'

        return return_on_err

    def process_list(self, token):
        output = []

        for (value,) in token.value:
            output.append(self.process_element(value, value.value))

        return output

    def process_dict(self, dict_):
        output = {}

        for key, value in dict_.value.items():
            output[key.value] = self.process_element(value, value.value)

        return output


def parse(raw_json):
    json_parser = JsonParser(raw_json)

    return json_parser.parse()
