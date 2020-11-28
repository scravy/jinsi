import re
from typing import Callable


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def head(obj):
    return next(iter(obj))


def select(obj, *path, fallback=None):
    current = obj
    for element in path:
        try:
            current = current[element]
        except (KeyError, TypeError):
            return fallback
    return current


def substitute(thing, callback: Callable[[str], str]):
    if isinstance(thing, (type(None), bool, int, float)):
        return thing
    if isinstance(thing, str):
        fs = re.split("{(\\$?[a-zA-Z0-9-_]+)}", thing)
        result = []
        is_even = True
        for f in fs:
            is_even = not is_even
            if is_even:
                result.append(callback(f))
            else:
                result.append(f)
        return "".join(result)
    elif isinstance(thing, list):
        result = []
        for item in thing:
            result.append(substitute(item, callback))
        return result
    else:
        result = {}
        for key, value in thing.items():
            key = substitute(key, callback)
            value = substitute(value, callback)
            result[key] = value
        return result
