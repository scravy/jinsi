import textwrap
from json.decoder import JSONDecodeError
from typing import Dict, Iterator

from yaml import YAMLError

from .jsonutil import loadjson_all, dumpjson
from .nodes import Constant, Empty, Node
from .parser import Parser, Environment
from .util import treat
from .value import Value
from .yamlutil import dumpyaml, loadyaml_all


def _evaluate(node: Node, *, args: Dict) -> Value:
    return node.evaluate(env=Environment(**args))


def _parse(doc: Value) -> Node:
    if not isinstance(doc, (list, dict)):
        return Constant(parent=Empty(), value=doc)
    return Parser().parse_node(doc, parent=Empty())


def _parse_json(s: str) -> Iterator[Node]:
    docs = loadjson_all(s)
    for doc in docs:
        yield _parse(doc)


def _parse_string(s: str) -> Iterator[Node]:
    s = textwrap.dedent(s)
    docs = loadyaml_all(s)
    count = 0
    try:
        for doc in docs:
            count += 1
            yield _parse(doc)
    except YAMLError as err:
        if count < 2:
            try:
                skip = 0
                it = _parse_json(s)
                while skip < count:
                    skip += 1
                    next(it)
                    continue
                yield from it
            except JSONDecodeError:
                raise err
        else:
            raise err


# noinspection PyShadowingBuiltins
def _parse_file(path: str, *, _open) -> Iterator[Node]:
    with _open(path) as f:
        docs = loadyaml_all(f)
        for doc in docs:
            yield _parse(doc)


def _render(node: Node, *, args: Dict, as_json: bool) -> str:
    value = _evaluate(node, args=args)
    if as_json:
        return dumpjson(value)
    else:
        return dumpyaml(value)


def render_string(s: str, *, args: Dict = None, as_json: bool = False) -> Iterator[str]:
    """Render each document from a string and return each rendered string one by one."""
    if not args:
        args = {}
    for node in _parse_string(s):
        yield _render(node, args=args, as_json=as_json)


def render_file(path: str, *, args: Dict = None, as_json: bool = False, _open=open) -> Iterator[str]:
    """Render each document from a file and return each rendered string one by one."""
    if not args:
        args = {}
    for node in _parse_file(path, _open=_open):
        yield _render(node, args=args, as_json=as_json)


def _render1(it: Iterator[str], as_json: bool) -> str:
    r = []
    if as_json:
        for doc in it:
            r.append(doc)
            r.append('\n')
    else:
        r.append(next(it))
        r.append("\n")
        for doc in it:
            r.append("\n--\n")
            r.append(doc)
    return "".join(r)


def render1s(s: str, *, args: Dict = None, as_json: bool = False) -> str:
    """Load all documents from a string and render them as string."""
    return _render1(render_string(s, args=args, as_json=as_json), as_json=as_json)


def render1f(path: str, *, args: Dict = None, as_json: bool = False) -> str:
    """Load all documents from a file and render them as string."""
    return _render1(render_file(path, args=args, as_json=as_json), as_json=as_json)


def load_string(s: str, *, args: Dict = None, numtype: type = float) -> Iterator[Value]:
    """Load all documents from a string."""
    if not args:
        args = {}
    docs = loadyaml_all(textwrap.dedent(s))
    for doc in docs:
        node = _parse(doc)
        value = _evaluate(node, args=args)
        yield treat(value, numtype=numtype)


def load_file(path: str, *, args: Dict = None, numtype: type = float, _open=open) -> Iterator[Value]:
    """Load all documents from a path."""
    if not args:
        args = {}
    with _open(path) as file:
        docs = loadyaml_all(file)
        for doc in docs:
            node = _parse(doc)
            value = _evaluate(node, args=args)
            yield treat(value, numtype=numtype)


def load1s(s: str, *, args: Dict = None, numtype: type = float) -> Value:
    """Load a single document from a string."""
    r, = load_string(s, args=args, numtype=numtype)
    return r


def load1f(path: str, *, args: Dict = None, numtype: type = float) -> Value:
    """Load a single document from a file."""
    r, = load_file(path, args=args, numtype=numtype)
    return r
