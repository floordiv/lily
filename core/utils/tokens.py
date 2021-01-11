from copy import deepcopy
from types import ModuleType
from importlib import import_module

from core.utils.contexts import Context
from core.utils.tools import create_token, process_escape_characters
from core.utils.tokentypes import (IF_BLOCK, ELIF_BLOCK, ELSE_BLOCK,
                                   FUNCASSIGN, VARASSIGN, FCALL,
                                   BRANCH, WHILE_LOOP, FOR_LOOP,
                                   RETURN_STATEMENT, BREAK_STATEMENT,
                                   CONTINUE_STATEMENT, VARIABLE, MATHEXPR,
                                   IMPORT_STATEMENT, CLASSASSIGN, CLASSINSTANCE,
                                   LIST, TUPLE, EXECUTE_CODE, EVALUATE_CODE,
                                   STRING, PARENTHESIS, TRY_EXCEPT_BLOCK,
                                   PYIMPORT_STATEMENT)


class BasicToken:
    def __init__(self, context, typeof, value, unary='+', primary_type=None, lineno=None):
        self.context = context
        self.type = typeof
        self.value: any = value
        self.unary = unary
        self.primary_type = primary_type or typeof
        self.priority = 0
        self.exclam = False  # also known as `!var`. If true, value has to be swapped
        self.lineno = lineno

    def clone(self):
        value = self.value

        if isinstance(value, list):
            value = value.copy()

        token = BasicToken(self.context, self.type, value, unary=self.unary, primary_type=self.primary_type)
        token.priority = self.priority
        token.exclam = self.exclam

        return token

    def as_json(self):
        return {
            'context': self.context,
            'type': self.type,
            'primary_type': self.primary_type,
            'value': self.value,
            'unary': self.unary,
            'priority': self.priority,
            'exclam': self.exclam,
            'lineno': self.lineno,
        }

    def __str__(self):
        try:
            value = int(self.unary + str(self.value)) if self.unary != '+' else self.value
        except ValueError:
            value = self.value

        return f'{self.primary_type or self.type}({repr(value)})'

    __repr__ = __str__


class FunctionCall:
    def __init__(self, evaluator, func_name, args, kwargs, unary, lineno):
        self.evaluator = evaluator
        self.name = func_name
        self.args = args
        self.kwargs = kwargs
        self.unary = unary
        self.lineno = lineno

        self.type = self.primary_type = FCALL

    def execute(self, context):
        func = context[self.name]
        args = []
        kwargs = {}

        for arg in self.args:
            if arg.type == VARIABLE or arg.primary_type == PARENTHESIS:
                arg_value = self.evaluator([arg], context=context)
            elif arg.type == MATHEXPR:
                arg_value = self.evaluator(arg.value, context)
            elif hasattr(arg, 'execute'):
                arg_value = arg.execute(context)
            else:
                arg_value = arg.value

            args.append(arg_value)

        for kwvar, kwval in self.kwargs.items():
            if kwval.type == VARIABLE:
                kwval = context[kwval.value]

            if isinstance(kwval, BasicToken):
                kwval = kwval.value

            kwargs[kwvar.value] = kwval

        return func(*args, **kwargs)

    def __str__(self):
        return f'FunctionCall(name={self.name}, args={self.args})'

    __repr__ = __str__


class Function:
    def __init__(self, executor, func_name, args, kwargs, code, lineno):
        self.executor = executor
        self.name = func_name
        self.args = args
        self.kwargs = kwargs
        self.code = code
        self.extend_args = ()
        self.lineno = lineno

        self.expected_args = len(args)
        self.type = self.primary_type = FUNCASSIGN

    def __call__(self, *args, **kwargs):
        given_args_len = len(args) + len(self.extend_args)

        if self.expected_args != given_args_len:
            raise TypeError(f'{self.name}: expected {self.expected_args} arguments, {given_args_len} got instead')

        temp_context = Context()

        for arg, given_arg in zip(self.args, self.extend_args + args):
            temp_context[arg.value] = given_arg

        for default_kw_var, default_kw_val in self.kwargs.items():
            temp_context[default_kw_var.value] = default_kw_val

        for kw_var, kw_val in kwargs.items():
            if kw_var not in self.kwargs:
                raise TypeError(f'{self.name}: got an unexpected kwarg: {kw_var}')

            temp_context[kw_var] = kw_val

        executor_response = self.executor(self.code, temp_context)

        if executor_response is None:
            value = None
        elif executor_response.type == RETURN_STATEMENT:
            value = executor_response.value
        else:
            raise SyntaxError('unexpected return token type: ' + executor_response.type)

        return value

    def execute(self, context):
        context[self.name] = self

    def __str__(self):
        return f'{self.name}({self.args}, {self.kwargs})'

    __repr__ = __str__


class Class:
    def __init__(self, context, executor, name, body, lineno):
        self.context = context
        self.executor = executor
        self.name = name
        self.body = self.value = body
        self.lineno = lineno

        self.type = self.primary_type = CLASSASSIGN

    def execute(self, context):
        self.context = context
        context[self.name] = self

    def __call__(self, *init_args, **init_kwargs):
        """
        In case of classes, this execute is playing a role of python's __new__ analog
        Custom __new__ functions are currently unsupported
        """

        return ClassInstance(self.executor, init_args, init_kwargs, self.body, self.lineno)


class ClassInstance:
    def __init__(self, executor, init_args, init_kwargs, body, lineno):
        self.instcontext = Context()
        self.executor = executor
        self.init_args = init_args
        self.init_kwargs = init_kwargs
        self.body = self.value = body
        self.lineno = lineno

        self.type = self.primary_type = CLASSINSTANCE

        self.extend_all_functions_with_cls_arg()
        # this initializes instance's context (assign functions, etc.)
        executor(body, context=self.instcontext)
        # finally! Time to call __init__ function
        self.init_instance()

    def __getattr__(self, item):
        if item == 'context':
            return self.instcontext

        item = self.instcontext[item]

        return item

    def __getattribute__(self, item):
        return object.__getattribute__(self, item)

    def init_instance(self):
        init = self.get_init_func()

        if init is not None:
            init(*self.init_args, **self.init_kwargs)

    def get_init_func(self):
        for token in self.body:
            if token.type == FUNCASSIGN and token.name == '__init__':
                return token

    def extend_all_functions_with_cls_arg(self):
        for token in self.body:
            if token.type == FUNCASSIGN:
                if not token.args:
                    raise SyntaxError('class method does not contains cls-method')

                token.extend_args = (self,)

    def __str__(self):
        return f'ClassInstance(context={self.instcontext})'


class Branch:
    def __init__(self, executor, evaluator, if_expr, *elif_exprs, else_expr=None):
        self.evaluator = evaluator
        self.executor = executor

        self.if_expr = if_expr
        self.elif_exprs = list(elif_exprs)
        self.else_expr = else_expr

        self.type = self.primary_type = BRANCH

    def get_branch(self, context):
        for branch in [self.if_expr] + self.elif_exprs:
            if self.evaluator(branch.expr, context):
                return branch

        return self.else_expr

    def execute(self, context):
        active_branch = self.get_branch(context)

        if active_branch is None:
            return

        return self.executor(active_branch.code, context)


class IfBranchLeaf:
    def __init__(self, expr, code, lineno):
        self.expr = deepcopy(expr)
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = IF_BLOCK

    def __str__(self):
        return f'IfBranch(expr={self.expr})'


class ElifBranchLeaf:
    def __init__(self, expr, code, lineno):
        self.expr = deepcopy(expr)
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = ELIF_BLOCK

    def __str__(self):
        return f'ElifBranch(expr={self.expr})'


class ElseBranchLeaf:
    def __init__(self, code, lineno):
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = ELSE_BLOCK

    def __str__(self):
        return str(self.code)


class ForLoop:
    def __init__(self, executor, evaluator, begin, end, step, code,
                 lineno):
        self.executor = executor
        self.evaluator = evaluator
        self.begin = begin
        self.end = deepcopy(end[0].value)
        self.step = step
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = FOR_LOOP

    def execute(self, context):
        # init loop
        self.begin.execute(context)

        while self.evaluator(self.end, context=context):
            executor_response = self.executor(self.code, context)

            if executor_response is not None:
                if executor_response.type == RETURN_STATEMENT:
                    return executor_response
                elif executor_response.type == BREAK_STATEMENT:
                    return

            self.step.execute(context)


class WhileLoop:
    def __init__(self, executor, evaluator, expr, code, lineno):
        self.executor = executor
        self.evaluator = evaluator
        self.expr = deepcopy(expr)
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = WHILE_LOOP

    def execute(self, context):
        while self.evaluator(self.expr, context=context):
            executor_response = self.executor(self.code, context=context)

            if executor_response is not None:
                if executor_response.type == RETURN_STATEMENT:
                    return executor_response
                elif executor_response.type == BREAK_STATEMENT:
                    return


class VarAssign:
    def __init__(self, evaluator, name, value, lineno):
        self.evaluator = evaluator
        self.name = name
        self.value = value
        self.lineno = lineno

        self.type = self.primary_type = VARASSIGN

    def execute(self, context):
        value = self.value

        if hasattr(value, 'execute'):
            value = value.execute(context)

            if not hasattr(value, 'primary_type') and not isinstance(value, ModuleType):
                value = create_token(context, BasicToken, ClassInstance, value)

        if hasattr(value, 'primary_type') and value.type == MATHEXPR:
            value = self.evaluator(value.value, context, return_token=True)

        if hasattr(self.name, 'primary_type') and self.name.type == TUPLE:
            if value.type not in (LIST, TUPLE):
                raise TypeError('only lists and tuples can be unpacked')

            to_assign = zip(self.name.value, value.value)
        else:
            to_assign = [[self.name, value]]

        for var, val in to_assign:
            if var.type != VARIABLE:
                raise SyntaxError('assigning value to non-variable')
            elif hasattr(val, 'primary_type') and val.type == MATHEXPR:
                val = val.value

            if hasattr(val, 'primary_type') and val.type in (CLASSASSIGN, CLASSINSTANCE):
                result = val
            else:
                if not isinstance(val, list):
                    val = [val]

                result = self.evaluator(val, context)

            context[var.value] = result

    def __str__(self):
        return f'VarAssign(name={repr(self.name)}, value={repr(self.value)})'

    __repr__ = __str__


class ReturnStatement:
    def __init__(self, evaluator, value, lineno, dont_evaluate_value=False):
        self.evaluator = evaluator
        self.value = value
        self.lineno = lineno

        self.type = self.primary_type = RETURN_STATEMENT
        self.value_already_evaluated = dont_evaluate_value

    def execute_value(self, context):
        if not self.value_already_evaluated:
            self.value = self.evaluator(self.value, context=context)
            self.value_already_evaluated = True

        return self.value

    def __str__(self):
        return f'RETURN({repr(self.value)})'

    __repr__ = __str__


class BreakStatement:
    def __init__(self, lineno):
        self.type = self.primary_type = BREAK_STATEMENT
        self.lineno = lineno

    def __str__(self):
        return 'BREAK'

    __repr__ = __str__


class ContinueStatement:
    def __init__(self, lineno):
        self.type = self.primary_type = CONTINUE_STATEMENT
        self.lineno = lineno

    def __str__(self):
        return 'CONTINUE'

    __repr__ = __str__


class ImportStatement:
    def __init__(self, path, name, lineno):
        self.path = self.value = path + '.lt'
        self.name = name
        self.lineno = lineno

        self.type = self.primary_type = IMPORT_STATEMENT

    def __str__(self):
        return f'IMPORT({self.name}:{self.path})'

    __repr__ = __str__


class PyimportStatement:
    def __init__(self, path, name, lineno):
        self.path = self.value = path
        self.name = name
        self.lineno = lineno

        self.type = self.primary_type = PYIMPORT_STATEMENT

    def execute(self, context):
        context[self.name] = import_module(self.path)

    def __str__(self):
        return f'IMPORT({self.name}:{self.path})'

    __repr__ = __str__


class ExecuteCode:
    def __init__(self, executor, semantic_parser, code, lineno):
        self.executor = executor
        self.semantic_parser = semantic_parser
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = EXECUTE_CODE

    def execute(self, context):
        from core.lexer.lexer import Lexer

        if self.code.type == STRING:
            raw_code = self.code.value
        elif self.code.type == VARIABLE:
            raw_code = context[self.code.value]
        elif hasattr(self.code, 'execute'):
            raw_code = self.code.execute(context)
        else:
            raise TypeError('only string or variable can be given to exec')

        if (hasattr(raw_code, 'primary_type') and raw_code.type != STRING)\
                or not isinstance(raw_code, str):
            raise SyntaxError('only string can be given to exec')

        # raw_code now is string (I hope)
        lexer = Lexer(process_escape_characters(raw_code))
        code = lexer.parse(context=context)

        return self.executor(self.semantic_parser(code), context=context)


class EvaluateCode:
    def __init__(self, evaluator, semantic_parser, code,
                 lineno):
        self.evaluator = evaluator
        self.semantic_parser = semantic_parser
        self.code = code
        self.lineno = lineno

        self.type = self.primary_type = EVALUATE_CODE

    def execute(self, context):
        from core.lexer.lexer import Lexer

        if self.code.type == STRING:
            raw_code = self.code.value
        elif self.code.type == VARIABLE:
            raw_code = context[self.code.value]
        elif hasattr(self.code, 'execute'):
            raw_code = self.code.execute()
        else:
            raise TypeError('only string or variable can be given to exec')

        if (hasattr(raw_code, 'primary_type') and raw_code.type != STRING)\
                or not isinstance(raw_code, str):
            raise SyntaxError('only string can be given to exec')

        # raw_code now is string (I hope)
        lexer = Lexer(process_escape_characters(raw_code))
        code = lexer.parse(context=context)

        return self.evaluator(self.semantic_parser(code), context=context)


class TryExceptBlock:
    def __init__(self, executor, code, errhandler, lineno):
        self.executor = executor
        self.code = code
        self.errhandler = errhandler
        self.lineno = lineno

        self.type = self.primary_type = TRY_EXCEPT_BLOCK

    def execute(self, context):
        try:
            self.executor(self.code, context=context)
        except:
            self.executor(self.errhandler, context=context)
