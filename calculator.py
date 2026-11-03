"""Безопасный вычислитель простых арифметических выражений без eval."""
import ast
import operator
import math

BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
          ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculate(expression):
    if len(expression) > 150:
        raise ValueError('Слишком длинное выражение')
    tree = ast.parse(expression, mode='eval')
    def walk(node, depth=0):
        if depth > 20:
            raise ValueError('Слишком сложное выражение')
        if isinstance(node, ast.Expression):
            return walk(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            val = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in BINARY:
            val = BINARY[type(node.op)](walk(node.left, depth + 1), walk(node.right, depth + 1))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
            val = UNARY[type(node.op)](walk(node.operand, depth + 1))
        else:
            raise ValueError('Разрешены только числа и +, -, *, /, //, %, скобки')
        if abs(val) > 10**12 or not math.isfinite(val):
            raise ValueError('Результат слишком большой')
        return val
    return walk(tree)


def response(expression):
    try:
        return {'result': calculate(expression)}
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
        return {'error': str(exc)}
