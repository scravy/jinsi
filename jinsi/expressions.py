import re
from decimal import Decimal

from .functions import Functions
from .nodes import *


def peek(stack):
    return stack[-1] if stack else None


PRECEDENCES = {
    'or': 1,
    'and': 2,
    '==': 3,
    '!=': 3,
    '<': 4,
    '<=': 4,
    '>': 5,
    '>=': 5,
    '+': 6,
    '-': 6,
    '*': 7,
    '/': 7,
}


# noinspection PyDefaultArgument
def greater_precedence(op1, op2, precedences=PRECEDENCES):
    return precedences[op1] > precedences[op2]


FUNCTIONS = {
    'or': Functions.or_,
    'and': Functions.and_,
    '==': Functions.eq,
    '!=': Functions.neq,
    '<': Functions.lt,
    '>': Functions.gt,
    '<=': Functions.lte,
    '>=': Functions.gte,
    '+': Functions.add,
    '-': Functions.sub,
    '*': Functions.mul,
    '/': Functions.div,
}


# noinspection PyDefaultArgument
def build_node(operators: List[str], nodes: List[Node], functions=FUNCTIONS):
    operator = operators.pop()
    right = nodes.pop()
    left = nodes.pop()
    func = functions[operator]
    node = FunctionApplication(parent=Empty(), function=func)
    node.args = [left, right]
    left.parent = node
    right.parent = node
    nodes.append(node)


DIGITS = frozenset(x for x in "0123456789")


def is_digit(char, digits=DIGITS):
    return char in digits


LETTERS = frozenset(x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


def is_letter(char, letters=LETTERS):
    return char in letters


def is_env_var(name, regex=re.compile(r"^[0-9_]*[A-Z][_A-Z0-9]*$")):
    return regex.match(name)


def parse_expression(
        expr: str,
        parent: Node,
        _regex=re.compile(r"-?[0-9]+|-?[0-9]+\\.[0-9]+|-?\$?[a-zA-Z][a-zA-Z0-9._-]*|[+/*()<>=!-]+"),
) -> Node:
    tokens = _regex.findall(expr)
    nodes = []
    operators = []
    for token in tokens:
        if token[0].isdigit() or (len(token) > 1 and token[0] == '-' and token[1].isdigit()):
            nodes.append(Constant(parent=Empty(), value=Decimal(token)))
        elif token[0].isalpha() and token not in ('and', 'or'):
            if is_env_var(token):
                nodes.append(GetEnvVar(parent=Empty(), name=token))
            else:
                nodes.append(GetLet(parent=Empty(), path=token.split(".")))
        elif token[0] == '$':
            nodes.append(GetDyn(parent=Empty(), path=token[1:].split(".")))
        elif token == '(':
            operators.append(token)
        elif token == ')':
            top = peek(operators)
            while top is not None and top != '(':
                build_node(operators, nodes)
                top = peek(operators)
            operators.pop()  # Discard the '('
        else:
            top = peek(operators)
            while top is not None and top not in "()" and greater_precedence(top, token):
                build_node(operators, nodes)
                top = peek(operators)
            operators.append(token)
    while peek(operators) is not None:
        build_node(operators, nodes)
    # TODO: handle error if len(nodes) != 1
    result = nodes[0]
    result.parent = parent
    return result
