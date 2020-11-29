from __future__ import annotations

from typing import Dict, List, Any

from .environment import Environment
from .exceptions import NoSuchVariableError
from .util import Singleton, select, substitute

Value = Any


class Node:
    is_empty = False

    def __init__(self, parent: Node):
        self.parent: Node = parent
        self.is_empty = False

    def get_let(self, name: str, env: Environment) -> Any:
        return self.parent.get_let(name, env)

    def eval(self, env: Environment) -> Value:
        pass


class Empty(Node, metaclass=Singleton):
    is_empty = True

    def __init__(self):
        super().__init__(self)

    def get_let(self, name: str, env: Environment) -> Any:
        raise NoSuchVariableError(name)


class Constant(Node):
    def __init__(self, parent: Node, value: Value):
        super().__init__(parent)
        self.value = value

    def eval(self, env: Dict[str, Any]) -> Value:
        return self.value


class GetLet(Node):
    def __init__(self, parent: Node, path: List[str]):
        super().__init__(parent)
        self.path: List[str] = path

    def eval(self, env: Environment) -> Value:
        result = self.get_let(self.path[0], env)
        if len(self.path) > 1:
            result = select(result, *self.path[1:])
        return result


class GetEnv(Node):
    def __init__(self, parent: Node, path: List[str]):
        super().__init__(parent)
        self.path: List[str] = path

    def eval(self, env: Environment) -> Value:
        result = env.get_env(self.path[0])
        if len(self.path) > 1:
            result = select(result, *self.path[1:])
        return result


class Let(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.let: Dict[str, Node] = {}
        self.env: Dict[str, Value] = {}
        self.body: Node = Empty()

    def eval(self, env: Environment) -> Value:
        if not self.env:
            return self.body.eval(env)
        my_env: Dict[str, Value] = {}
        for key, node in self.env.items():
            my_env[key] = node.eval(env)
        return self.body.eval(env.with_env(my_env))

    def get_let(self, name: str, env: Environment):
        if name not in self.let:
            return super().get_let(name, env)
        return self.let[name].eval(env)


class Else(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.body: Node = Empty()
        self.otherwise: Node = Empty()

    def eval(self, env: Environment) -> Value:
        result = self.body.eval(env)
        if isinstance(result, (list, dict, str)) and len(result) == 0 \
                or isinstance(result, bool) and not result \
                or result is None:
            result = self.otherwise.eval(env)
        return result


class Object(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.children: Dict[str, Node] = {}

    def eval(self, env: Environment) -> Value:
        result = {}
        for key, node in self.children.items():
            result[key] = node.eval(env)
        return result


class Sequence(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.elements: List[Node] = []

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

    def eval(self, env: Environment) -> Value:
        my_env: Dict[str, Value] = {}
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


class Format(Node):
    def __init__(self, parent: Node, value: Value):
        super().__init__(parent)
        self.value: Value = value

    def eval(self, env: Environment) -> Value:
        def subst(key: str) -> str:
            if key[:1] == "$":
                return env.get_env(key[1:])
            return self.get_let(key, env)

        return substitute(self.value, subst)
