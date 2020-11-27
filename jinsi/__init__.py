from __future__ import annotations

from datetime import date, datetime
from inspect import getattr_static
from typing import Dict, List, Any, Union

import yaml

from .exceptions import JinsiException, NoSuchEnvironmentVariable, NoSuchFunction, NoParse
from .functions import Functions
from .util import head, Singleton

Value = Any


class Environment(object):
    def __init__(self, env: Dict[str, Value], parent: Union[type(None), Environment] = None):
        self.parent = parent
        self.env: Dict[str, Value] = env

    def get_env(self, key: str) -> Value:
        if key in self.env:
            return self.env[key]
        if self.parent:
            return self.parent.get_env(key)
        raise NoSuchEnvironmentVariable()

    def with_env(self, env: Dict[str, Value]) -> Environment:
        return Environment(env, self)


class Node(object):
    is_empty = False

    def __init__(self, parent: Node):
        self.parent: Node = parent
        self.is_empty = False

    @staticmethod
    def parse(obj: Any, parent: Node) -> Node:
        if isinstance(obj, list):
            return Sequence.parse(obj, parent)
        if isinstance(obj, (type(None), bool, int, float, str, date, datetime)):
            return Constant.parse(obj, parent)
        if '::ref' in obj:
            ref = obj['::ref']
            if ref[:1] == '$':
                return GetEnv.parse(obj, parent)
            return GetLet.parse(obj, parent)
        if '::let' in obj:
            return Let.parse(obj, parent)
        if '::env' in obj:
            return Env.parse(obj, parent)
        for key in obj:
            if key[:6] == "::call":
                return Application.parse(obj, parent)
            if key[:6] == "::each":
                return Each.parse(obj, parent)
            if key[:2] == "::":
                return FunctionApplication.parse(obj, parent)
        return Object.parse(obj, parent)

    def get_let(self, name: str, env: Environment) -> Any:
        return self.parent.get_let(name, env)

    def get_let_lazy(self, name: str) -> Node:
        return self.parent.get_let_lazy(name)

    def eval(self, env: Environment) -> Value:
        pass


class Empty(Node, metaclass=Singleton):
    is_empty = True

    def __init__(self):
        super().__init__(self)

    def get_let(self, name: str, env: Environment) -> Any:
        raise KeyError(name)

    def get_let_lazy(self, name: str) -> Node:
        raise KeyError(name)


class Constant(Node):
    def __init__(self, parent: Node, value: Value):
        super().__init__(parent)
        self.value = value

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        return Constant(parent, obj)

    def eval(self, env: Dict[str, Any]) -> Value:
        return self.value


class GetLet(Node):
    def __init__(self, parent: Node, what: str):
        super().__init__(parent)
        self.what: str = what

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        return GetLet(parent, obj['::ref'])

    def eval(self, env: Environment) -> Value:
        return self.get_let(self.what, env)


class GetEnv(Node):
    def __init__(self, parent: Node, what: str):
        super().__init__(parent)
        self.what: str = what

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        return GetEnv(parent, obj['::ref'][1:])

    def eval(self, env: Environment) -> Value:
        return env.get_env(self.what)


class Let(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.let: Dict[str, Node] = {}
        self.body: Node = Empty()

    @staticmethod
    def parse(obj: Any, parent: Node) -> Node:
        node = Let(parent)
        remainder = {}
        for key, value in obj.items():
            if key == '::let':
                for let_key, let_value in value.items():
                    node.let[let_key] = Node.parse(let_value, node)
                continue
            remainder[key] = value
        node.body = Node.parse(remainder, node)
        return node

    def eval(self, env: Environment) -> Value:
        return self.body.eval(env)

    def get_let(self, name: str, env: Environment):
        if name not in self.let:
            return super().get_let(name, env)
        return self.let[name].eval(env)


class Env(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.env: Dict[str, Node] = {}
        self.body: Node = Empty()

    @staticmethod
    def parse(obj: Any, parent: Node) -> Node:
        node = Env(parent)
        remainder = {}
        for key, value in obj.items():
            if key == '::env':
                for env_key, env_value in value.items():
                    node.env[env_key] = Node.parse(env_value, node)
                continue
            remainder[key] = value
        node.body = Node.parse(remainder, node)
        return node

    def eval(self, env: Environment) -> Value:
        my_env = {}
        for key, value in self.env.items():
            my_env[key] = value.eval(env)
        return self.body.eval(env.with_env(my_env))


class Object(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.children: Dict[str, Node] = {}

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        node = Object(parent)
        for key, value in obj.items():
            node.children[key] = Node.parse(value, node)
        return node

    def eval(self, env: Environment) -> Value:
        result = {}
        for key, node in self.children.items():
            result[key] = node.eval(env)
        return result


class Sequence(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.elements: List[Node] = []

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        seq = Sequence(parent)
        for item in obj:
            seq.elements.append(Node.parse(item, seq))
        return seq

    def eval(self, env: Environment) -> Value:
        result = []
        for element in self.elements:
            result.append(element.eval(env))
        return result


class FunctionApplication(Node):
    def __init__(self, parent: Node, function):
        super().__init__(parent)
        self.function = function
        self.args: List[Node] = []

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        for key in obj:
            if key in ("::let", "::env"):
                continue
            if key[:2] == "::":
                name = key[2:]
                if name[-1:] == "_":
                    name = name[:-1]
                try:
                    if not isinstance(getattr_static(Functions, name), staticmethod):
                        raise NoSuchFunction(name)
                except AttributeError:
                    raise NoSuchFunction(name)
                func = getattr(Functions, name)
                app = FunctionApplication(parent, func)
                args = obj[key]
                if isinstance(args, list):
                    for arg in args:
                        app.args.append(Node.parse(arg, app))
                elif len(args) == 1:
                    app.args.append(Node.parse(args, app))
                else:
                    raise JinsiException()
                return app
        raise JinsiException()

    def eval(self, env: Environment) -> Value:
        args = []
        for arg in self.args:
            args.append(arg.eval(env))
        result = self.function(*args)
        return result


class Application(Node):
    def __init__(self, parent: Node, template: str):
        super().__init__(parent)
        self.template = template
        self.kwargs: Dict[str, Node] = {}

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        for key in obj:
            if key[:6] == "::call":
                _, name = key.split(" ")
                app = Application(parent, name)
                if isinstance(obj[key], list):
                    app.kwargs[""] = Sequence.parse(obj[key], app)
                else:
                    for arg_key, arg_value in obj[key].items():
                        app.kwargs[arg_key] = Node.parse(arg_value, app)
                return app
        raise JinsiException()

    def eval(self, env: Environment) -> Value:
        my_env: Dict[str, Any] = {}
        for key, node in self.kwargs.items():
            my_env[key] = node.eval(env)
        return self.get_let(self.template, env.with_env(my_env))


class Each(Node):
    def __init__(self, parent: Node, source: str, target: str):
        super().__init__(parent)
        self.source: str = source
        self.target: str = target
        self.body: Node = Empty()
        self._value = None

    @staticmethod
    def parse(obj, parent: Node) -> Node:
        for key in obj:
            if key[:6] == "::each":
                _, source, _, target = key.split(" ")
                each = Each(parent, source, target)
                each.body = Node.parse(obj[key], each)
                return each
        raise NoParse()

    def get_let(self, name: str, env: Environment) -> Value:
        if name == self.target:
            return self._value
        else:
            return super().get_let(name, env)

    def eval(self, env: Environment) -> Value:
        if self.source[:1] == "$":
            value = env.get_env(self.source[1:])
        else:
            value = self.parent.get_let(self.source, env)
        results = []
        if self.target[:1] == "$":
            target = self.target[1:]
            for entry in value:
                result = self.body.eval(env.with_env({target: entry}))
                results.append(result)
        else:
            for entry in value:
                self._value = entry
                result = self.body.eval(env)
                results.append(result)
        return results


def parse(doc) -> Node:
    return Node.parse(doc, Empty())


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


def load_yaml(yaml_str: str) -> Node:
    import textwrap
    yaml_str = textwrap.dedent(yaml_str)
    doc = yaml.safe_load(yaml_str)
    return parse(doc)


def load_file(file: str) -> Node:
    with open(file) as f:
        doc = yaml.safe_load(f)
    return parse(doc)
