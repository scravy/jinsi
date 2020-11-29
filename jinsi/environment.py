from __future__ import annotations

from typing import Dict, Any, Union

from .exceptions import NoSuchEnvironmentVariableError

Value = Any


class Environment:
    def __init__(self, env: Dict[str, Value], parent: Union[type(None), Environment] = None):
        self.parent = parent
        self.env: Dict[str, Value] = env

    def get_env(self, key: str) -> Value:
        if key in self.env:
            return self.env[key]
        if self.parent:
            return self.parent.get_env(key)
        raise NoSuchEnvironmentVariableError(key)

    def with_env(self, env: Dict[str, Value]) -> Environment:
        return Environment(env, self)
