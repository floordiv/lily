from sys import argv, path
from os.path import abspath
path.append(abspath('..'))

from core.interpreter.interpreter import interpret, init_paths


if __name__ == '__main__':
    init_paths(change_cwd=False)

    with open(argv[1]) as fd:
        interpret(fd.read())
