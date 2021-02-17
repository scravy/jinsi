from __future__ import annotations

from typing import Dict, List, Tuple

from .environment import Environment
from .exceptions import NoSuchVariableError, NoSuchEnvironmentVariableError, NoCaseError
from .util import Singleton, select, substitute, empty, cached_method
from .value import Value


class Node:
    is_empty = False

    def __init__(self, parent: Node):
        self.parent: Node = parent
        self.is_empty = False

    def get_let(self, name: str) -> Node:
        return self.parent.get_let(name)

    def evaluate(self, env: Environment) -> Value:
        return None


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

    def evaluate(self, env: Dict[str, Value]) -> Value:
        return self.value


class GetLet(Node):
    def __init__(self, parent: Node, path: List[str]):
        super().__init__(parent)
        self.path: List[str] = path

    def evaluate(self, env: Environment) -> Value:
        result = self.get_let(self.path[0]).evaluate(env)
        if len(self.path) > 1:
            result = select(result, *self.path[1:])
        return result


class GetDyn(Node):
    def __init__(self, parent: Node, path: List[str]):
        super().__init__(parent)
        self.path: List[str] = path

    def evaluate(self, env: Environment) -> Value:
        result = env.get_dyn(self.path[0])
        if len(self.path) > 1:
            result = select(result, *self.path[1:])
        return result


class GetEnvVar(Node):
    def __init__(self, parent: Node, name: str):
        super().__init__(parent)
        self.name: str = name

    def evaluate(self, env: Environment) -> Value:
        return env.get_var(self.name)


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


class Else(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.body: Node = Empty()
        self.otherwise: Node = Empty()

    def evaluate_body(self, env: Environment):
        # noinspection PyBroadException
        try:
            return self.body.evaluate(env)
        except (NoSuchEnvironmentVariableError, ArithmeticError, ValueError, TypeError, LookupError):
            return None
        except Exception as exc:
            print(f"WARNING: Unexpected exception {exc}")
            return None

    def evaluate(self, env: Environment) -> Value:
        result = self.evaluate_body(env)
        if empty(result):
            result = self.otherwise.evaluate(env)
        return result


class Object(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.children: Dict[str, Node] = {}

    def evaluate(self, env: Environment) -> Value:
        result = {}
        for key, node in self.children.items():
            key_f = Format(self, key).evaluate(env)
            result[key_f] = node.evaluate(env)
        return result


class Sequence(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.elements: List[Node] = []

    def evaluate(self, env: Environment) -> Value:
        result = []
        for element in self.elements:
            result.append(element.evaluate(env))
        return result


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


class Application(Node):
    def __init__(self, parent: Node, template: str):
        super().__init__(parent)
        self.template = template
        self.kwargs: Dict[str, Node] = {}

    @cached_method
    def evaluate(self, env: Environment) -> Value:
        my_env: Dict[str, Value] = {}
        for key, node in self.kwargs.items():
            my_env[key] = node.evaluate(env)
        return self.get_let(self.template).evaluate(env.with_env(my_env))


class Each(Node):
    def __init__(self, parent: Node, source: str, target: str):
        super().__init__(parent)
        self.source: str = source
        self.target: str = target
        self.body: Node = Empty()
        self._value: Node = Empty()

    def get_let(self, name: str) -> Node:
        if name == self.target:
            return self._value
        else:
            return super().get_let(name)

    def evaluate(self, env: Environment) -> Value:
        if self.source[:1] == "$":
            value = env.get_dyn(self.source[1:])
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
                self._value: Node = Constant(self, entry)
                result = self.body.evaluate(env)
                results.append(result)
        return results


class When(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.when: Node = Empty()
        self.then: Node = Empty()
        self.else_: Node = Empty()

    def evaluate(self, env: Environment) -> Value:
        if not empty(self.when.evaluate(env)):
            return self.then.evaluate(env)
        else:
            return self.else_.evaluate(env)


class All(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.nodes: List[Node] = []

    def evaluate(self, env: Environment) -> Value:
        for node in self.nodes:
            if empty(node.evaluate(env)):
                return False
        return True


class Any(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.nodes: List[Node] = []

    def evaluate(self, env: Environment) -> Value:
        for node in self.nodes:
            result = node.evaluate(env)
            if not empty(result):
                return result
        return False


class Case(Node):
    def __init__(self, parent: Node):
        super().__init__(parent)
        self.cases: List[Tuple[Node, Node]] = []

    def evaluate(self, env: Environment) -> Value:
        for condition, action in self.cases:
            if condition.evaluate(env):
                return action.evaluate(env)
        raise NoCaseError()


class Format(Node):
    def __init__(self, parent: Node, value: Value):
        super().__init__(parent)
        self.value: Value = value

    def evaluate(self, env: Environment) -> Value:
        def subst(key: str) -> str:
            if key[:1] == "$":
                getter = GetDyn(parent=self, path=key[1:].split("."))
            else:
                getter = GetLet(parent=self, path=key.split("."))
            result = getter.evaluate(env)
            return str(result)

        return substitute(self.value, subst)
