from __future__ import annotations

import yaml

from .environment import Environment
from .exceptions import JinsiException, NoSuchEnvironmentVariableError, NoSuchFunctionError, NoParseError, \
    NoSuchVariableError, MalformedNameError
from .functions import Functions
from .nodes import Node, Empty, Value
from .parser import Parser
from .util import head, Singleton, select, substitute, merge


def parse(doc, parent: Node = Empty()) -> Node:
    return Parser().parse_node(doc, parent)


def evaluate(node: Node) -> Value:
    return node.eval(Environment({}))


def process(yaml_doc) -> Value:
    return evaluate(parse(yaml_doc))


def render(yaml_str: str) -> str:
    node = load_yaml(yaml_str)
    return yaml.safe_dump(evaluate(node))


def render_yaml(yaml_doc) -> str:
    return yaml.safe_dump(evaluate(parse(yaml_doc)))


def render_file(file: str) -> str:
    node = load_file(file)
    return yaml.safe_dump(evaluate(node))


def load_yaml(yaml_str: str, parent: Node = Empty()) -> Node:
    import textwrap
    yaml_str = textwrap.dedent(yaml_str)
    doc = yaml.safe_load(yaml_str)
    return parse(doc, parent)


def load_file(file: str, parent: Node = Empty()) -> Node:
    with open(file) as f:
        doc = yaml.safe_load(f)
    return parse(doc, parent)
