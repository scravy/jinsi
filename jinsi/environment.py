from __future__ import annotations

from typing import Dict, Any

from .exceptions import NoSuchEnvironmentVariableError

Value = Any


class Environment:
    def __init__(self):
        self.env: Dict[str, Value] = {}

    def get_env(self, key: str) -> Value:
        if key in self.env:
            return self.env[key]
        raise NoSuchEnvironmentVariableError(key)

    def with_env(self, env: Dict[str, Value]) -> Environment:
        new_env = Environment()
        for key, value in self.env.items():
            new_env.env[key] = value
        for key, value in env.items():
            new_env.env[key] = value
        return new_env
