from __future__ import annotations

import os
from typing import Dict, Any as Value

from .exceptions import NoSuchEnvironmentVariableError


class Environment:
    def __init__(self, **env):
        self.dyn: Dict[str, Value] = {}
        for key, value in env.items():
            self.dyn[key] = value

    @staticmethod
    def get_var(key: str) -> Value:
        return os.getenv(key)

    def get_dyn(self, key: str) -> Value:
        if key in self.dyn:
            return self.dyn[key]
        raise NoSuchEnvironmentVariableError(key)

    def with_env(self, env: Dict[str, Value]) -> Environment:
        new_env = Environment()
        for key, value in self.dyn.items():
            new_env.dyn[key] = value
        for key, value in env.items():
            new_env.dyn[key] = value
        return new_env
