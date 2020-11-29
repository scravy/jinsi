from __future__ import annotations

from typing import Dict, List, Any, FrozenSet

from .environment import Environment
from .exceptions import NoSuchVariableError
from .util import Singleton, select, substitute, cached_method

Value = Any


class Node:
    is_empty = False

    def __init__(self, parent: Node):
        self.parent: Node = parent
        self.is_empty = False

    def get_let(self, name: str) -> Node:
        return self.parent.get_let(name)

    def evaluate(self, env: Environment) -> Value:
        pass

    def requires_env(self) -> FrozenSet[str]:
        return frozenset()


class Empty(Node, metaclass=Singleton):
    is_empty = True

    def __init__(self):
        super().__init__(self)

    def get_let(self, name: str) -> Node:
        raise NoSuchVariableError(name)


class Constant(Node):
    def __init__(self, parent: Node, value: Value):
        super().__init__(parent)
        self.value = value

    def evaluate(self, env: Dict[str, Any]) -> Value:
        return self.value


class GetLet(Node):
    def __init__(self, parent: Node, path: List[str]):
        super().__init__(parent)
        self.path: List[str] = path

    def evaluate(self, env: Environment) -> Value:
        result = self.get_let(self.path[0]).evaluate(env)
        if len(self.path) > 1:
            # TODO: Should this be more strict - right now select() gracefully falls back to None
            result = select(result, *self.path[1:])
        return result


class GetEnv(Node):
    def __init__(self, parent: Node, path: List[str]):
        super().__init__(parent)
        self.path: List[str] = path

    def evaluate(self, env: Environment) -> Value:
        result = env.get_env(self.path[0])
        if len(self.path) > 1:
            result = select(result, *self.path[1:])
        return result

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        return frozenset([self.path[0]])


class Let(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.let: Dict[str, Node] = {}
        self.env: Dict[str, Node] = {}
        self.body: Node = Empty()

    def evaluate(self, env: Environment) -> Value:
        if not self.env:
            return self.body.evaluate(env)
        my_env: Dict[str, Value] = {}
        for key, node in self.env.items():
            my_env[key] = node.evaluate(env)
        return self.body.evaluate(env.with_env(my_env))

    def get_let(self, name: str) -> Node:
        if name not in self.let:
            return super().get_let(name)
        return self.let[name]

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set(self.body.requires_env())
        for node in self.env.values():
            result.update(node.requires_env())
        for name in self.env.keys():
            try:
                result.remove(name)
            except KeyError:
                # TODO: This could be a warning - env defined but not consumed
                pass
        return frozenset(result)


class Else(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.body: Node = Empty()
        self.otherwise: Node = Empty()

    def evaluate(self, env: Environment) -> Value:
        # noinspection PyBroadException
        try:
            result = self.body.evaluate(env)
        except Exception:
            # TODO: Should this method actually catch exceptions or merely default empty values?
            result = None
        if self.empty(result):
            result = self.otherwise.evaluate(env)
        return result

    @staticmethod
    def empty(result) -> bool:
        if isinstance(result, (list, dict, str)) and len(result) == 0:
            return True
        if isinstance(result, bool) and not result:
            return True
        return result is None

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set(self.body.requires_env())
        result.update(self.otherwise.requires_env())
        return frozenset(result)


class Object(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.children: Dict[str, Node] = {}

    def evaluate(self, env: Environment) -> Value:
        result = {}
        for key, node in self.children.items():
            result[key] = node.evaluate(env)
        return result

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set()
        for node in self.children.values():
            result.update(node.requires_env())
        return frozenset(result)


class Sequence(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.elements: List[Node] = []

    def evaluate(self, env: Environment) -> Value:
        result = []
        for element in self.elements:
            result.append(element.evaluate(env))
        return result

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set()
        for node in self.elements:
            result.update(node.requires_env())
        return frozenset(result)


class FunctionApplication(Node):
    def __init__(self, parent: Node, function):
        super().__init__(parent)
        self.function = function
        self.args: List[Node] = []

    def evaluate(self, env: Environment) -> Value:
        args = []
        for arg in self.args:
            args.append(arg.evaluate(env))
        result = self.function(*args)
        return result

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set()
        for node in self.args:
            result.update(node.requires_env())
        return frozenset(result)


class Application(Node):
    def __init__(self, parent: Node, template: str):
        super().__init__(parent)
        self.template = template
        self.kwargs: Dict[str, Node] = {}

    def evaluate(self, env: Environment) -> Value:
        my_env: Dict[str, Value] = {}
        for key, node in self.kwargs.items():
            my_env[key] = node.evaluate(env)
        return self.get_let(self.template).evaluate(env.with_env(my_env))

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set(self.get_let(self.template).requires_env())
        for name in self.kwargs.keys():
            try:
                result.remove(name)
            except KeyError:
                # TODO: this could be a warning - template does not use this argument
                pass
        return frozenset(result)


class Each(Node):
    def __init__(self, parent: Node, source: str, target: str):
        super().__init__(parent)
        self.source: str = source
        self.target: str = target
        self.body: Node = Empty()
        self._value: Value = None

    def get_let(self, name: str) -> Node:
        if name == self.target:
            return self._value
        else:
            return super().get_let(name)

    def evaluate(self, env: Environment) -> Value:
        if self.source[:1] == "$":
            value = env.get_env(self.source[1:])
        else:
            value = self.parent.get_let(self.source).evaluate(env)
        results = []
        if self.target[:1] == "$":
            target = self.target[1:]
            for entry in value:
                result = self.body.evaluate(env.with_env({target: entry}))
                results.append(result)
        else:
            for entry in value:
                self._value = entry
                result = self.body.evaluate(env)
                results.append(result)
        return results

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set(self.body.requires_env())
        if self.target[:1] == "$":
            result.add(self.target[1:])
        return frozenset(result)


class Format(Node):
    def __init__(self, parent: Node, value: Value):
        super().__init__(parent)
        self.value: Value = value

    def evaluate(self, env: Environment) -> Value:
        def subst(key: str) -> str:
            if key[:1] == "$":
                return env.get_env(key[1:])
            return self.get_let(key).evaluate(env)

        return substitute(self.value, subst)

    @cached_method
    def requires_env(self) -> FrozenSet[str]:
        result = set()

        def record(key: str) -> str:
            if key[:1] == "$":
                result.add(key[1:])
            return ""

        substitute(self.value, record)
        return frozenset(result)
