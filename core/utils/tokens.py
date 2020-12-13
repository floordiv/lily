from copy import deepcopy

from lily.core.utils.tokentypes import (IF_BLOCK, ELIF_BLOCK, ELSE_BLOCK,
                                        FUNCASSIGN, VARASSIGN, FCALL,
                                        BRANCH, WHILE_LOOP, FOR_LOOP,
                                        CODE, RETURN_STATEMENT, BREAK_STATEMENT,
                                        CONTINUE_STATEMENT, VARIABLE, MATHEXPR,
                                        IMPORT_STATEMENT)


class BasicToken:
    def __init__(self, context, typeof, value, unary='+', primary_type=None):
        self.context = context
        self.type = typeof
        self.value: any = value
        self.unary = unary
        self.primary_type = primary_type or typeof
        self.priority = 0
        self.exclam = False  # also known as `!var`. If true, value has to be swapped

    def clone(self):
        value = self.value

        if isinstance(value, list):
            value = value.copy()

        token = BasicToken(self.context, self.type, value, unary=self.unary, primary_type=self.primary_type)
        token.priority = self.priority
        token.exclam = self.exclam

        return token

    def __str__(self):
        try:
            value = int(self.unary + str(self.value)) if self.unary != '+' else self.value
        except ValueError:
            value = self.value

        return f'{self.primary_type or self.type}({repr(value)})'

    __repr__ = __str__


class FunctionCall:
    def __init__(self, context, evaluator, func_name, args, kwargs, unary):
        self.context = context
        self.evaluator = evaluator
        self.name = func_name
        self.args = args
        self.kwargs = kwargs
        self.unary = unary

        self.type = self.primary_type = FCALL

    def execute(self):
        func = self.context[self.name]
        args = []
        kwargs = {}

        for arg in self.args:
            if arg.type == VARIABLE:
                arg_value = self.evaluator([arg], context=self.context)
                # arg_value = self.context[arg.value]
            elif arg.type == MATHEXPR:
                arg_value = self.evaluator(arg.value, self.context)
            elif hasattr(arg, 'execute'):
                arg_value = arg.execute()
            else:
                arg_value = arg.value

            args.append(arg_value)

        for kwvar, kwval in self.kwargs.items():
            if kwval.type == VARIABLE:
                kwval = self.context[kwval.value]

            if isinstance(kwval, BasicToken):
                kwval = kwval.value

            kwargs[kwvar] = kwval

        return func(*args, **kwargs)

    def __str__(self):
        return f'FunctionCall(name={self.name}, args={self.args})'

    __repr__ = __str__


class Function:
    def __init__(self, context, executor, func_name, args, kwargs, code):
        self.context = context
        self.executor = executor
        self.name = func_name
        self.args = args
        self.kwargs = kwargs
        self.code = code

        self.expected_args = len(args)
        self.type = self.primary_type = FUNCASSIGN

    def __call__(self, *args, **kwargs):
        given_args_len = len(args)

        if self.expected_args != given_args_len:
            raise TypeError(f'{self.name}: expected {self.expected_args} arguments, {given_args_len} got instead')

        for arg, given_arg in zip(self.args, args):
            self.context[arg.value] = given_arg

        for default_kw_var, default_kw_val in self.kwargs.items():
            self.context[default_kw_var] = default_kw_val

        for kw_var, kw_val in kwargs.items():
            if kw_var not in self.kwargs:
                raise TypeError(f'{self.name}: got an unexpected kwarg: {kw_var}')

            self.context[kw_var] = kw_val

        executor_response = self.executor(self.code, self.context)

        if executor_response is None:
            value = None
        elif executor_response.type != RETURN_STATEMENT:
            raise SyntaxError('unexpected return token type: ' + executor_response.type)
        else:
            value = executor_response.value

        return value

    def execute(self):
        self.context[self.name] = self


class Branch:
    def __init__(self, context, executor, evaluator, if_expr, *elif_exprs, else_expr=None):
        self.context = context
        self.evaluator = evaluator
        self.executor = executor

        self.if_expr = if_expr
        self.elif_exprs = list(elif_exprs)
        self.else_expr = else_expr

        self.type = self.primary_type = BRANCH

    def get_branch(self):
        for branch in [self.if_expr] + self.elif_exprs:
            if self.evaluator(branch.expr.copy(), self.context):
                return branch

        return self.else_expr

    def execute(self):
        active_branch = self.get_branch()

        if active_branch is None:
            return

        return self.executor(active_branch.code, self.context)


class IfBranchLeaf:
    def __init__(self, expr, code):
        self.expr = deepcopy(expr)
        self.code = code

        self.type = self.primary_type = IF_BLOCK

    def __str__(self):
        return f'IfBranch(expr={self.expr})'


class ElifBranchLeaf:
    def __init__(self, expr, code):
        self.expr = deepcopy(expr)
        self.code = code

        self.type = self.primary_type = ELIF_BLOCK

    def __str__(self):
        return f'ElifBranch(expr={self.expr})'


class ElseBranchLeaf:
    def __init__(self, code):
        self.code = code

        self.type = self.primary_type = ELSE_BLOCK

    def __str__(self):
        return str(self.code)


class Code:
    def __init__(self, context, executor, raw):
        self.context = context
        # executor executes already parsed code. It is a function from interpreter or like that
        self.executor = executor
        self.raw = raw

        self.type = self.primary_type = CODE

    def execute(self, context=None):
        if context is None:
            context = self.context

        return self.executor(context, self.raw)


class ForLoop:
    def __init__(self, context, executor, evaluator, begin, end, step, code):
        self.context = context
        self.executor = executor
        self.evaluator = evaluator
        self.begin = begin
        self.end = deepcopy(end[0].value)
        self.step = step
        self.code = code

        self.type = self.primary_type = FOR_LOOP

    def execute(self):
        # init loop
        self.begin.execute()

        while self.evaluator(self.end, context=self.context):
            executor_response = self.executor(self.code, self.context)

            if executor_response is not None:
                if executor_response.type == RETURN_STATEMENT:
                    return executor_response
                elif executor_response.type == BREAK_STATEMENT:
                    return

            self.step.execute()


class WhileLoop:
    def __init__(self, context, executor, evaluator, expr, code):
        self.context = context
        self.executor = executor
        self.evaluator = evaluator
        self.expr = deepcopy(expr)
        self.code = code

        self.type = self.primary_type = WHILE_LOOP

    def execute(self):
        while self.evaluator(self.expr, context=self.context):
            executor_response = self.executor(self.code, context=self.context)

            if executor_response is not None:
                if executor_response.type == RETURN_STATEMENT:
                    return executor_response
                elif executor_response.type == BREAK_STATEMENT:
                    return


class VarAssign:
    def __init__(self, context, evaluator, name, value):
        if value.type == MATHEXPR:
            value = value.value

        self.context = context
        self.evaluator = evaluator
        self.name = name
        self.value = value

        self.type = self.primary_type = VARASSIGN

    def execute(self):
        value = self.value

        if not isinstance(value, list):
            value = [value]

        value = self.evaluator(value, context=self.context)
        self.context[self.name] = value

    def __str__(self):
        return f'VarAssign(name={repr(self.name)}, value={repr(self.value)})'

    __repr__ = __str__


class ReturnStatement:
    def __init__(self, context, evaluator, value):
        self.context = context
        self.evaluator = evaluator
        self.value = value

        self.type = self.primary_type = RETURN_STATEMENT
        self.value_already_executed = False

    def execute_value(self):
        if not self.value_already_executed:
            self.value = self.evaluator(self.value, context=self.context)
            self.value_already_executed = True

        return self.value

    def __str__(self):
        return f'RETURN({repr(self.value)})'

    __repr__ = __str__


class BreakStatement:
    def __init__(self):
        self.type = BREAK_STATEMENT

    def __str__(self):
        return 'BREAK'

    __repr__ = __str__


class ContinueStatement:
    def __init__(self):
        self.type = self.primary_type = CONTINUE_STATEMENT

    def __str__(self):
        return 'CONTINUE'

    __repr__ = __str__


class ImportStatement:
    def __init__(self, path, name):
        self.path = self.value = path + '.lt'
        self.name = name

        self.type = self.primary_type = IMPORT_STATEMENT

    def __str__(self):
        return f'IMPORT({self.name}:{self.path})'

    __repr__ = __str__

