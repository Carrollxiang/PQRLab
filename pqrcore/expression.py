# -*- coding: utf-8 -*-
"""
Created on 2020-04-02

@author: 张宽

将字符串表达式解析为S-表达式
将S-表达式反解析为字符串表达式
简化、计算S-表达式
"""

from math import *
from operator import *
import ast


def isname(name):
    try:
        name = ast.parse(name)
    except SyntaxError:
        return False
    name = name.body
    if len(name) != 1:
        return False
    name = name[0]
    if not isinstance(name, ast.Expr):
        return False
    name = name.value
    return isinstance(name, ast.Name)


class ParsedExpression():
    """
    S-表达式
    cls.__func_dict = {func: (op, prec), ...}
        func - 操作符对应函数名 (str类)
        op - 操作符 (str类)
        prec - 操作优先级
    self.__expr = (func, *args)
        func - 函数名 (str类)
        arg - 参数 (分形结构，底层为int,float,complex的数字，或str的变量)
    """
    __func_dict = {
        'or_': ('|', 0),
        'xor': ('^', 1),
        'and_': ('&', 2),
        'lshift': ('<<', 3),
        'rshift': ('>>', 3),
        'add': ('+', 4),
        'sub': ('-', 4),
        'mul': ('*', 5),
        'truediv': ('/', 5),
        'floordiv': ('//', 5),
        'mod': ('%', 5),
        'pos': ('+', 6),
        'neg': ('-', 6),
        'invert': ('~', 6),
        'pow': ('**', 7)}

    def __init__(self, expr):
        def parse_ast(expr):
            """将AST表达式解析为S-表达式"""
            # BinOp类型 (e.g. 1 + 2 -> ('+', 1, 2))
            if isinstance(expr, ast.BinOp):
                op_dict = {
                    ast.Add: 'add',
                    ast.Sub: 'sub',
                    ast.Mult: 'mul',
                    ast.Div: 'truediv',
                    ast.Mod: 'mod',
                    ast.Pow: 'pow',
                    ast.LShift: 'lshift',
                    ast.RShift: 'rshift',
                    ast.BitOr: 'or_',
                    ast.BitXor: 'xor',
                    ast.BitAnd: 'and_',
                    ast.FloorDiv: 'floordiv'}
                left = parse_ast(expr.left)
                right = parse_ast(expr.right)
                op = op_dict[type(expr.op)]
                return op, left, right
            # UnaryOp类型 (e.g. -x -> ('-', 'x'))
            if isinstance(expr, ast.UnaryOp):
                op_dict = {
                    ast.Invert: 'invert',
                    ast.UAdd: 'pos',
                    ast.USub: 'neg'}
                operand = parse_ast(expr.operand)
                op = op_dict[type(expr.op)]
                return op, operand
            # Call类型 (e.g. cos(pi) -> ('cos', 'pi'))
            if isinstance(expr, ast.Call):
                args = [parse_ast(arg) for arg in expr.args]
                func = expr.func.id
                return (func, *args)
            # Num类型 (e.g. 0 -> 0)
            if isinstance(expr, ast.Num):
                n = expr.n
                return n
            # Name类型 (e.g. x -> 'x')
            if isinstance(expr, ast.Name):
                id = expr.id
                return id
            # 其它
            raise SyntaxError('AST表达式解析失败')

        if isinstance(expr, str):
            expr = ast.parse(expr).body
            err = SyntaxError('非数学表达式')
            if len(expr) != 1:
                raise err
            expr = expr[0]
            if not isinstance(expr, ast.Expr):
                raise err
            expr = expr.value
            self.__expr = parse_ast(expr)
            return
        self.expression = expr

    def __str__(self):
        def deparse(expr):
            """将S-表达式反解析为(字符串, 函数优先级)"""
            if not isinstance(expr, tuple):
                return str(expr), 8
            func, *args = expr
            # 0个参数
            if args == ():
                return '%s()' % func, 8
            func, prec = self.__func_dict.get(func, (func, -1))
            arg, *args = args
            arg, prec_child = deparse(arg)
            if prec_child < prec:
                arg = '(%s)' % arg
            # 1个参数
            if args == ():
                # 函数不能化为运算符
                if prec < 0:
                    expr = '%s(%s)' % (func, arg)
                    prec = 8
                # 函数能化为运算符
                else:
                    expr = func + arg
                return expr, prec
            expr = arg
            # 函数不能化为运算符
            if prec < 0:
                for arg in args:
                    arg = deparse(arg)[0]
                    expr += ',%s' % arg
                expr = '%s(%s)' % (func, expr)
                prec = 8
            # 函数能化为运算符
            else:
                for arg in args:
                    arg, prec_child = deparse(arg)
                    if prec_child <= prec:
                        arg = '(%s)' % arg
                    expr += func + arg
            return expr, prec

        return deparse(self.__expr)[0]

    def __call__(self, **rules):
        def eval(expr, **rules):
            """计算S-表达式"""
            if not isinstance(expr, tuple):
                if isinstance(expr, str):
                    rules = {**globals(), **rules}
                    expr = rules[expr]
                    if not isinstance(expr, (int, float, complex)):
                        raise TypeError('表达式底层参数应为数字')
                return expr
            func, *args = expr
            args = [eval(arg, **rules) for arg in args]
            rules = {**globals(), **rules}
            func = rules[func]
            return func(*args)

        return eval(self.__expr, **rules)

    def __eq__(self, other):
        if not isinstance(other, ParsedExpression):
            return False
        other = self.__simplify(other.__expr)
        return self.__simplify(self.__expr) == other

    def __pos__(self):
        expr = self.__new__(ParsedExpression)
        expr.__expr = ('pos', self.__expr)
        return expr

    def __neg__(self):
        expr = self.__new__(ParsedExpression)
        expr.__expr = ('neg', self.__expr)
        return expr

    def __invert__(self):
        expr = self.__new__(ParsedExpression)
        expr.__expr = ('invert', self.__expr)
        return expr

    def __add__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('add', self.__expr, other.__expr)
        return expr

    def __radd__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('add', other.__expr, self.__expr)
        return expr

    def __iadd__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('add', self.__expr, other.__expr)
        return self

    def __sub__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('sub', self.__expr, other.__expr)
        return expr

    def __rsub__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('sub', other.__expr, self.__expr)
        return expr

    def __isub__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('sub', self.__expr, other.__expr)
        return self

    def __mul__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('mul', self.__expr, other.__expr)
        return expr

    def __rmul__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('mul', other.__expr, self.__expr)
        return expr

    def __imul__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('mul', self.__expr, other.__expr)
        return self

    def __truediv__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('truediv', self.__expr, other.__expr)
        return expr

    def __rtruediv__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('truediv', other.__expr, self.__expr)
        return expr

    def __itruediv__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('truediv', self.__expr, other.__expr)
        return self

    def __floordiv__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('floordiv', self.__expr, other.__expr)
        return expr

    def __rfloordiv__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('floordiv', other.__expr, self.__expr)
        return expr

    def __ifloordiv__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('floordiv', self.__expr, other.__expr)
        return self

    def __mod__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('mod', self.__expr, other.__expr)
        return expr

    def __rmod__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('mod', other.__expr, self.__expr)
        return expr

    def __imod__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('mod', self.__expr, other.__expr)
        return self

    def __pow__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('pow', self.__expr, other.__expr)
        return expr

    def __rpow__(self, other):
        if isinstance(other, ParsedExpression):
            expr = self.__new__(ParsedExpression)
        else:
            expr = other = ParsedExpression(other)
        expr.__expr = ('pow', other.__expr, self.__expr)
        return expr

    def __ipow__(self, other):
        if not isinstance(other, ParsedExpression):
            other = ParsedExpression(other)
        self.__expr = ('pow', self.__expr, other.__expr)
        return self

    @property
    def expression(self):
        return self.__expr

    @expression.setter
    def expression(self, expr):
        def check(expr):
            """检查S-表达式"""
            if not isinstance(expr, tuple):
                if isinstance(expr, (int, float, complex)):
                    return
                if isinstance(expr, str):
                    if isname(expr):
                        return
                    raise SyntaxError('表达式底层字符串应为变量')
                raise TypeError('表达式底层参数应为数字或字符串')
            func, *args = expr
            if not isinstance(func, str):
                raise TypeError('表达式函数名应为字符串')
            if not isname(func):
                raise SyntaxError('表达式函数名不合法')
            for arg in args:
                check(arg)

        check(expr)
        self.__expr = expr

    @staticmethod
    def __simplify(expr):
        """化简S-表达式"""
        if not isinstance(expr, tuple):
            if isinstance(expr, str):
                try:
                    val = globals()[expr]
                except KeyError:
                    pass
                else:
                    if isinstance(val, (int, float, complex)):
                        expr = val
            return expr
        args = []
        isnum = True
        for arg in expr[1:]:
            arg = ParsedExpression.__simplify(arg)
            args.append(arg)
            if isinstance(arg, (str, tuple)):
                isnum = False
        func = expr[0]
        if isnum:
            try:
                val = globals()[func]
            except KeyError:
                pass
            else:
                val = val(*args)
                if isinstance(val, (int, float, complex)):
                    return val
        return (func, *args)

    def simplify(self):
        """化简self.expression"""
        self.__expr = self.__simplify(self.__expr)
