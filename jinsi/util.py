from __future__ import annotations

import functools
import re
from typing import Callable, List

from jinsi.exceptions import NoMergePossible


def cachedmethod(func):
    @functools.wraps(func)
    def wrapper(self):
        try:
            cache = self.__method_cache__
        except AttributeError:
            self.__method_cache__ = {}
            cache = self.__method_cache__
        name = func.__name__
        try:
            result = cache[name]
        except KeyError:
            result = func(self)
            cache[name] = result
        return result

    return wrapper


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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
        fs = re.split("<<(\\$?[a-zA-Z0-9-_]+)>>", thing)
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


def merge(*objects):
    if all(isinstance(item, list) for item in objects):
        result = []
        for ls in objects:
            for item in ls:
                result.append(item)
        return result
    if not all(isinstance(item, dict) for item in objects):
        raise NoMergePossible()
    result = {}
    for obj in objects:
        for key, value in obj.items():
            if key not in result:
                result[key] = value
                continue
            if isinstance(value, list):
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
            if isinstance(result[key], list):
                if isinstance(value, list):
                    for item in value:
                        result[key].append(item)
                    continue
                result[key].append(value)
                continue
            if isinstance(result[key], dict):
                if not isinstance(value, dict):
                    raise NoMergePossible()
                for item_key, item_value in value.items():
                    result[key][item_key] = item_value
                continue
            result[key] = value
    return result


def parse_name(name) -> List[str]:
    parts = []
    for p1 in str(name).split("-"):
        for part in p1.split("_"):
            current_part = []
            last_was_upper = False
            for char in part:
                if char.isupper() and not last_was_upper:
                    if current_part:
                        parts.append("".join(current_part).lower())
                    current_part = []
                elif char.islower() and last_was_upper:
                    last = current_part.pop()
                    if current_part:
                        parts.append("".join(current_part).lower())
                    current_part = [last]
                current_part.append(char)
                last_was_upper = char.isupper()
            if current_part:
                parts.append("".join(current_part).lower())
    return parts


def empty(result) -> bool:
    if isinstance(result, (bool, list, dict, str)):
        return not result
    return result is None
