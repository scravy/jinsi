from __future__ import annotations

import functools
import math
import re
from typing import Callable, List, Union

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


class Dec(tuple):
    __slots__ = []

    def __new__(cls, value: Union[bool, int, float, str, Dec], scale: int = None) -> Dec:
        if scale is not None:
            if scale < 0:
                raise ValueError(scale)
            if not isinstance(value, int):
                raise TypeError(value)
        elif isinstance(value, Dec):
            return value
        elif isinstance(value, str):
            if re.match("^-?[0-9]+$", value):
                value = int(value)
                scale = 0
            elif re.match("^-?[0-9]+\\.[0-9]+$", value):
                a, b = value.split(".")
                value = int(a) * (10 ** len(b)) + int(b)
                scale = len(b)
            else:
                raise ValueError(value)
        elif isinstance(value, int):
            scale = 0
        elif isinstance(value, float):
            return Dec(str(value))
        elif isinstance(value, bool):
            if value:
                return Dec(1)
            else:
                return Dec(0)
        while scale > 0 and value % 10 == 0:
            scale -= 1
            value //= 10
        # noinspection PyTypeChecker
        return tuple.__new__(cls, (value, scale))

    @property
    def value(self) -> int:
        return tuple.__getitem__(self, 0)

    @property
    def scale(self) -> int:
        return tuple.__getitem__(self, 1)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.scale > 0:
            value = str(self.value)
            v1 = value[:-self.scale]
            if v1 == "":
                v1 = "0"
            elif v1 == "-":
                v1 = "-0"
            return f"{v1}.{value[-self.scale:]}"
        else:
            return str(self.value)

    def __int__(self) -> int:
        return self.value // (10 ** self.scale)

    def __bool__(self) -> bool:
        return self.value != 0

    def __getitem__(self, item):
        raise TypeError

    @staticmethod
    def _scaled(this, that,
                func: Callable[[int, int], int],
                scale_func: Callable[[int, int], int] = max,
                rescale: bool = True,
                result_constructor=None):
        if not isinstance(this, Dec):
            this = Dec(this)
        if not isinstance(that, Dec):
            that = Dec(that)
        target_scale = scale_func(this.scale, that.scale)
        if rescale:
            this_diff = target_scale - this.scale
            that_diff = target_scale - that.scale
            this_value = this.value * (10 ** this_diff) if this_diff > 0 else this.value
            that_value = that.value * (10 ** that_diff) if that_diff > 0 else that.value
        else:
            this_value = this.value
            that_value = that.value
        result = func(this_value, that_value)
        if result_constructor is not None:
            return result_constructor(result, target_scale)
        return Dec(result, target_scale)

    def truncate(self, scale: int) -> Dec:
        if scale < 0:
            raise ValueError(scale)
        if scale >= self.scale:
            return self
        scale_diff = self.scale - scale
        target_value = self.value // (10 ** scale_diff)
        return Dec(target_value, scale)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Dec):
            return False
        return self.value == other.value and self.scale == other.scale

    def __ne__(self, other) -> bool:
        if not isinstance(other, Dec):
            return True
        return self.value != other.value or self.scale != other.scale

    def __lt__(self, other) -> bool:
        return self._scaled(self, other, lambda a, b: a < b, result_constructor=lambda a, _: bool(a))

    def __gt__(self, other) -> bool:
        return self._scaled(self, other, lambda a, b: a > b, result_constructor=lambda a, _: bool(a))

    def __le__(self, other) -> bool:
        return self._scaled(self, other, lambda a, b: a <= b, result_constructor=lambda a, _: bool(a))

    def __ge__(self, other) -> bool:
        return self._scaled(self, other, lambda a, b: a >= b, result_constructor=lambda a, _: bool(a))

    def __neg__(self) -> Dec:
        return Dec(-self.value, self.scale)

    def __abs__(self) -> Dec:
        return Dec(abs(self.value), self.scale)

    def __pos__(self) -> Dec:
        return self

    def __add__(self, other) -> Dec:
        return self._scaled(self, other, lambda a, b: a + b)

    def __sub__(self, other) -> Dec:
        return self._scaled(self, other, lambda a, b: a - b)

    def __mul__(self, other) -> Dec:
        return self._scaled(self, other, lambda a, b: a * b, lambda a, b: a + b, rescale=False)

    def __floordiv__(self, other) -> Dec:
        return Dec(int(self) // int(other))

    @staticmethod
    def div(this: Dec, that: Dec, maxscale: Union[int, type(None)] = None, minscale: int = 17) -> Dec:
        d1 = 10 ** this.scale
        d2 = 10 ** that.scale
        n = this.value * d2
        d = that.value * d1
        gcd = math.gcd(n, d)
        n //= gcd
        d //= gcd
        if d == 1:
            return Dec(n)

        matches = set()
        scale = 0
        value = 0
        while n != 0 and ((n, d) not in matches or scale < minscale) and (not maxscale or scale < maxscale):
            matches.add((n, d))
            value *= 10
            scale += 1
            n *= 10
            value += n // d
            n = n % d

        return Dec(value, scale)

    def __truediv__(self, other) -> Dec:
        return Dec.div(self, Dec(other))


if __name__ == '__main__':
    # x = Dec("2.7")
    # y = Dec("3.01")
    x = Dec(355)
    y = Dec(113)
    print(f"RES: {x / y}")
    print(f"RES: {355 / 113}")
