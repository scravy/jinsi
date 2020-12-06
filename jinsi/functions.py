import hashlib
from typing import Union, List

from dezimal import Dec

from .util import parse_name, select, empty


class Functions:

    @staticmethod
    def range_inclusive(from_, to):
        return [Dec(x) for x in range(int(from_), int(to) + 1)]

    @staticmethod
    def range_exclusive(from_, to):
        return [Dec(x) for x in range(int(from_), int(to))]

    # text functions

    @staticmethod
    def titlecase(value):
        return "".join(part.capitalize() for part in parse_name(value))

    @staticmethod
    def kebabcase(value):
        return "-".join(parse_name(value))

    @staticmethod
    def snakecase(value):
        return "_".join(parse_name(value))

    @staticmethod
    def camelcase(value):
        name = Functions.titlecase(value)
        return name[:1].lower() + name[1:]

    @staticmethod
    def uppercase(value):
        return str(value).upper()

    @staticmethod
    def lowercase(value):
        return str(value).lower()

    @staticmethod
    def trim(value, chars=None):
        return str(value).strip(chars)

    @staticmethod
    def trim_left(value, chars=None):
        return str(value).lstrip(chars)

    @staticmethod
    def trim_right(value, chars=None):
        return str(value).rstrip(chars)

    @staticmethod
    def pad_left(value: str, char: str, total_length: int):
        diff = total_length - len(value)
        if diff <= 0:
            return value
        return char * diff + value

    @staticmethod
    def pad_right(value: str, char: str, total_length: int):
        diff = total_length - len(value)
        if diff <= 0:
            return value
        return value + char * diff

    @staticmethod
    def explode(separator: str, value: str):
        return value.split(separator)

    @staticmethod
    def implode(separator: str, items: List):
        if not items:
            return ""
        result = []
        it = iter(items)
        head = next(it)
        result.append(head)
        for item in items:
            result.append(separator)
            result.append(item)
        return "".join(result)

    # hashes

    @staticmethod
    def md5(value):
        return hashlib.new("md5", value).hexdigest()

    @staticmethod
    def sha256(value):
        return hashlib.new("sha256", value).hexdigest()

    @staticmethod
    def sha512(value):
        return hashlib.new("sha512", value).hexdigest()

    @staticmethod
    def sha3_256(value):
        return hashlib.new("sha3_256", value).hexdigest()

    @staticmethod
    def sha3_512(value):
        return hashlib.new("sha3_512", value).hexdigest()

    @staticmethod
    def shake_128(value):
        return hashlib.new("shake_128", value).hexdigest()

    @staticmethod
    def shake_256(value):
        return hashlib.new("shake_256", value).hexdigest()

    # value tests

    @staticmethod
    def is_empty(value):
        return empty(value)

    # type tests

    @staticmethod
    def is_null(value):
        return value is None

    @staticmethod
    def is_number(value):
        return isinstance(value, (Dec, int, float))

    @staticmethod
    def is_string(value):
        return isinstance(value, str)

    @staticmethod
    def is_boolean(value):
        return isinstance(value, bool)

    @staticmethod
    def is_list(value):
        return isinstance(value, list)

    @staticmethod
    def is_object(value):
        return isinstance(value, dict)

    # data conversion

    @staticmethod
    def number(value):
        return Dec(value)

    @staticmethod
    def string(value):
        return str(value)

    @staticmethod
    def boolean(value):
        return bool(value)

    @staticmethod
    def list(value):
        if isinstance(value, list):
            return value
        return [value]

    # aggregation

    @staticmethod
    def sum(*args):
        result = Dec(0)
        for arg in args:
            result += Dec(arg)
        return result

    @staticmethod
    def product(*args):
        result = Dec(1)
        for arg in args:
            result *= Dec(arg)
        return result

    # comparison

    @staticmethod
    def eq(a, b):
        return a == b

    @staticmethod
    def neq(a, b):
        return a != b

    @staticmethod
    def lt(a, b):
        return a < b

    @staticmethod
    def gt(a, b):
        return a > b

    @staticmethod
    def lte(a, b):
        return a <= b

    @staticmethod
    def gte(a, b):
        return a >= b

    @staticmethod
    def and_(a, b):
        return a and b

    @staticmethod
    def or_(a, b):
        return a or b

    # arithmetic

    @staticmethod
    def add(a, b):
        return Dec(a) + Dec(b)

    @staticmethod
    def sub(a, b):
        return Dec(a) - Dec(b)

    @staticmethod
    def mul(a, b):
        return Dec(a) * Dec(b)

    @staticmethod
    def div(a, b, maxscale=None, minscale=17):
        return Dec.div(Dec(a), Dec(b), maxscale, minscale)

    # lists and strings

    @staticmethod
    def length(items):
        return len(items)

    @staticmethod
    def select(items, ix):
        return items[ix]

    @staticmethod
    def contains(needle, haystack):
        return needle in haystack

    @staticmethod
    def starts_with(prefix, value: Union[str, List]):
        for ix in range(0, len(prefix)):
            if prefix[ix] != value[ix]:
                return False
        return True

    @staticmethod
    def ends_with(prefix, value: Union[str, List]):
        for ix in range(1, len(prefix) + 1):
            if prefix[-ix] != value[-ix]:
                return False
        return True

    @staticmethod
    def reverse(items):
        return reversed(items)

    @staticmethod
    def sorted(key: str, items: list) -> list:
        path = key.split(".")

        def key(item):
            return select(item, *path)

        return sorted(items, key=key)

    @staticmethod
    def take(n: int, items):
        if not isinstance(items, list):
            items = str(items)
        return items[:int(n)]

    @staticmethod
    def drop(n: int, items):
        if not isinstance(items, list):
            items = str(items)
        return items[int(n):]

    @staticmethod
    def concat(*items):
        if all(isinstance(item, list) for item in items):
            result = []
            for ls in items:
                for item in ls:
                    result.append(item)
        return "".join([str(s) for s in items])

    # object creation utilities

    @staticmethod
    def object(key, value):
        return {key: value}

    @staticmethod
    def merge(*items):
        obj = {}
        for item in items:
            if item is None:
                continue
            if isinstance(item, list):
                item = Functions.merge(*item)
            for key, value in item.items():
                obj[key] = value
        return obj
