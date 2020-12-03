from __future__ import annotations

from typing import Union

import yaml

from .dec import Dec
from .environment import Environment
from .jsonutil import dumpjson
from .nodes import Node, Empty, Value, Constant
from .parser import Parser
from .util import Singleton, select, substitute, merge
from .yamlutil import Loader, Dumper


def parse(doc: Union[str, dict, list]) -> Node:
    if isinstance(doc, str):
        return load_yaml(doc)
    return Parser().parse_node(doc, Empty())


def evaluate(doc: Union[Node, str, dict, list], **env) -> Value:
    if not isinstance(doc, Node):
        doc: Node = parse(doc)
    return doc.evaluate(Environment(**env))


def render_yaml(doc: Union[Node, str, dict, list], **env) -> str:
    result = evaluate(doc, **env)
    return yaml.dump(result, Dumper=Dumper)


def render_file_yaml(file: str, **env) -> str:
    node = load_file(file)
    result = evaluate(node, **env)
    return yaml.dump(result, Dumper=Dumper)


def render_json(doc: Union[Node, str, dict, list], **env) -> str:
    result = evaluate(doc, **env)
    return dumpjson(result, indent=2)


def render_file_json(file: str, **env) -> str:
    node = load_file(file)
    result = evaluate(node, **env)
    return dumpjson(result, indent=2)


def load_yaml(yaml_str: str) -> Node:
    import textwrap
    yaml_str = textwrap.dedent(yaml_str)
    doc = yaml.load(yaml_str, Loader=Loader)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)


def load_file(file: str) -> Node:
    with open(file) as f:
        doc = yaml.load(f, Loader=Loader)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)
