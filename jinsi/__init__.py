from __future__ import annotations

import os.path
import textwrap
from typing import Union

import yaml

from .environment import Environment
from .jsonutil import dumpjson
from .nodes import Node, Empty, Value, Constant
from .parser import Parser
from .util import treat
from .yamlutil import Loader, Dumper, dumpyaml

# noinspection PyBroadException
try:
    PATH_MAX = os.pathconf('/', 'PC_PATH_MAX')
except Exception:
    PATH_MAX = 1024


def parse(doc: Union[str, dict, list]) -> Node:
    if isinstance(doc, str):
        return parse_yaml(doc)
    return Parser().parse_node(doc, Empty())


def parse_yaml(yaml_str: str) -> Node:
    import textwrap
    yaml_str = textwrap.dedent(yaml_str)
    doc = yaml.load(yaml_str, Loader=Loader)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)


def parse_file(path: str) -> Node:
    with open(path) as f:
        doc = yaml.load(f, Loader=Loader)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)


def parse_from(file_like) -> Node:
    doc = yaml.load(file_like, Loader=Loader)
    if not isinstance(doc, (list, dict)):
        return Constant(Empty(), doc)
    return parse(doc)


def evaluate(doc: Union[Node, str, dict, list], **env) -> Value:
    if not isinstance(doc, Node):
        doc: Node = parse(doc)
    return doc.evaluate(Environment(**env))


def render_yaml(doc: Union[Node, str, dict, list], **env) -> str:
    result = evaluate(doc, **env)
    return dumpyaml(result)


def render_file_yaml(file: str, **env) -> str:
    node = parse_file(file)
    result = evaluate(node, **env)
    return dumpyaml(result)


def render_json(doc: Union[Node, str, dict, list], **env) -> str:
    result = evaluate(doc, **env)
    return dumpjson(result)


def render_file_json(file: str, **env) -> str:
    node = parse_file(file)
    result = evaluate(node, **env)
    return dumpjson(result)


def load_yaml(yaml_str: str, *, numtype: type = float, **env) -> Value:
    doc = parse_yaml(textwrap.dedent(yaml_str))
    result = evaluate(doc, **env)
    return treat(result, numtype=numtype)


def load_file(path: str, *, numtype: type = float, **env) -> Value:
    doc = parse_file(path)
    result = evaluate(doc, **env)
    return treat(result, numtype=numtype)


def load_from(file_like, *, numtype: type = float, **env) -> Value:
    doc = parse_from(file_like)
    result = evaluate(doc, **env)
    return treat(result, numtype=numtype)


def load(thing, **env) -> Value:
    if isinstance(thing, str):
        if len(thing) <= PATH_MAX and os.path.exists(thing):
            return load_file(thing, **env)
        return load_yaml(thing, **env)
    return load_from(thing, **env)
