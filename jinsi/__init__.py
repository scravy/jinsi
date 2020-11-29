from __future__ import annotations

from typing import Union

import yaml

from .environment import Environment
from .nodes import Node, Empty, Value, Constant
from .parser import Parser
from .util import Singleton, select, substitute, merge


def parse(doc: Union[str, dict, list]) -> Node:
    if isinstance(doc, str):
        return load_yaml(doc)
    return Parser().parse_node(doc, Empty())


def evaluate(doc: Union[Node, str, dict, list]) -> Value:
    if not isinstance(doc, Node):
        doc: Node = parse(doc)
    return doc.evaluate(Environment())


def render(doc: Union[Node, str, dict, list]) -> str:
    return yaml.safe_dump(evaluate(doc))


def render_file(file: str) -> str:
    node = load_file(file)
    return yaml.safe_dump(evaluate(node))


def load_yaml(yaml_str: str) -> Node:
    import textwrap
    yaml_str = textwrap.dedent(yaml_str)
    doc = yaml.safe_load(yaml_str)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)


def load_file(file: str) -> Node:
    with open(file) as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)
