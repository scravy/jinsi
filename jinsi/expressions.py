import re

from .functions import Functions
from .nodes import *
from .util import Dec


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


def is_digit(x):
    return x in "0123456789"


def is_letter(x):
    return x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def parse_expression(expr: str, parent: Node) -> Node:
    tokens = re.findall(r"-?[0-9]+|-?[0-9]+\\.[0-9]+|[+/*()<>=!-]+|\$?[a-zA-Z][a-zA-Z0-9._-]*", expr)
    nodes = []
    operators = []
    for token in tokens:
        # TODO: handle get env var
        # TODO: handle -x (negated variable)
        if is_digit(token[0]) or (len(token) > 1 and token[0] == '-' and is_digit(token[1])):
            nodes.append(Constant(parent=Empty(), value=Dec(token)))
        elif is_letter(token[0]) and token not in ('and', 'or'):
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
