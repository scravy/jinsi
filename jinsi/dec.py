from __future__ import annotations

import re
import math
from typing import Union, Callable


class Dec(tuple):
    __slots__ = []

    def __new__(cls, value: Union[bool, int, float, str, Dec], scale: int = None):
        if scale is None:
            scale = 0
        else:
            if not isinstance(scale, int):
                raise TypeError(scale)
            if scale < 0:
                raise ValueError(scale)
        if isinstance(value, Dec):
            return value
        if isinstance(value, bool):
            return Dec(1) if value else Dec(0)
        if isinstance(value, float):
            value = str(value)
        if isinstance(value, str):
            return Dec.from_string(value)
        if not isinstance(value, int):
            if not isinstance(value, int):
                raise TypeError(f"when scale is given, value must be an int, but is {type(value)}: {value}")
        while scale > 0 and value % 10 == 0:
            scale -= 1
            value //= 10
        # noinspection PyTypeChecker
        return tuple.__new__(cls, (value, scale))

    @staticmethod
    def from_string(value: str) -> Dec:
        if re.match("^-?[0-9]+$", value):
            value = int(value)
            scale = 0
            return Dec(value, scale)
        elif re.match("^-?[0-9]+\\.[0-9]+$", value):
            a, b = value.split(".")
            value = int(a) * (10 ** len(b)) + int(b)
            scale = len(b)
            return Dec(value, scale)
        else:
            raise ValueError(value)

    @property
    def value(self):
        return tuple.__getitem__(self, 0)

    @property
    def scale(self):
        return tuple.__getitem__(self, 1)

    def __getitem__(self, key):
        raise TypeError

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

    def __float__(self) -> float:
        return self.value / 10 ** self.scale

    def __bool__(self) -> bool:
        return self.value != 0

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
            try:
                other = Dec(other)
            except TypeError:
                return False
        return self.value == other.value and self.scale == other.scale

    def __ne__(self, other) -> bool:
        try:
            other = Dec(other)
        except TypeError:
            return False
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
