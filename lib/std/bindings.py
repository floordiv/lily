from importlib import import_module


pybindings = {
    'true': True,
    'false': False,
    'null': None,
    'print': print,
    'input': input,
    'getattr': getattr,
    'hasattr': hasattr,
    'setattr': setattr,
    'pyimport': import_module,

    '__version__': (0, 0, 1),
    '__author__': 'floordiv',
    '__implementation__': 'lily',   # same as interpreter name
}
