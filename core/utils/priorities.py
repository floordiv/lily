MINIMAL = 1
MEDIUM = 2
HIGH = 3
MAXIMAL = 4


for_tokens = {
    '>': MINIMAL,
    '<': MINIMAL,
    '>=': MINIMAL,
    '<=': MINIMAL,
    '!=': MINIMAL,
    '&&': MINIMAL,
    '||': MINIMAL,
    '===': MINIMAL,  # TODO: === operator has to have higher priority. Choose it later

    '+': MEDIUM,
    '-': MEDIUM,
    '&': MEDIUM,
    '|': MEDIUM,
    '^': MEDIUM,
    '>>': MEDIUM,
    '<<': MEDIUM,
    '==': MEDIUM,

    '*': HIGH,
    '/': HIGH,
    '%': HIGH,
    '//': HIGH,

    '**': MAXIMAL,
}
