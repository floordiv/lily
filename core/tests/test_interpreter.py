from os import listdir

from core.interpreter.interpreter import interpret


def load_example(name):
    with open('./examples/' + name + '.lt') as example:
        return example.read()


def test_all(examples_dir='./examples/', exclude=None):
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
        print(example, '\n')

        with open(examples_dir + example) as example_fd:
            response = interpret(example_fd.read(), exit_after_execution=False, file=examples_dir + example)
            print('\n * exit-code:', response)

    print(splitline)


interpret(load_example('exceptions'), file='exceptions.lt')
# test_all(exclude=['simple_program_demo.lt', 'simple_echo_server.lt', 'simple_echo_client.lt'])
