import hashlib
from decimal import Decimal
from functools import reduce

from .jsonutil import dumpjson, loadjson
from .util import parse_name, empty


class Functions:

    @staticmethod
    def range_inclusive(from_, to):
        return [Decimal(x) for x in range(int(from_), int(to) + 1)]

    @staticmethod
    def range_exclusive(from_, to):
        return [Decimal(x) for x in range(int(from_), int(to))]

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
    def strip(value, chars):
        result = []
        for char in value:
            if char not in chars:
                result.append(char)
        return "".join(result)

    @staticmethod
    def _pad_prep(value, char, total_length):
        if not isinstance(value, str):
            value: str = str(value)
        if not isinstance(char, str):
            char: str = str(char)
        diff: int = int(total_length) - len(value)
        return char, diff, value

    @staticmethod
    def pad_left(value, char, total_length):
        char, diff, value = Functions._pad_prep(value, char, total_length)
        if diff <= 0:
            return value
        return char * diff + value

    @staticmethod
    def pad_right(value, char, total_length):
        char, diff, value = Functions._pad_prep(value, char, total_length)
        if diff <= 0:
            return value
        return value + char * diff

    @staticmethod
    def str_replace(needle, replacement, haystack):
        return str(haystack).replace(needle, replacement)

    @staticmethod
    def explode(separator, value):
        return value.split(separator)

    @staticmethod
    def implode(separator, items):
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
    def sha1(value):
        return hashlib.new("sha1", value).hexdigest()

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
        return isinstance(value, (Decimal, int, float))

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
        return Decimal(value)

    @staticmethod
    def string(value):
        return str(value)

    @staticmethod
    def integer(value):
        return int(value)

    @staticmethod
    def float(value):
        return float(value)

    @staticmethod
    def boolean(value):
        return bool(value)

    @staticmethod
    def list(value):
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def json_serialize(value):
        return dumpjson(value)

    @staticmethod
    def json_read(value):
        return loadjson(value)

    # aggregation

    @staticmethod
    def sum(*args):
        result = Decimal(0)
        for arg in args:
            result += Decimal(arg)
        return result

    @staticmethod
    def product(*args):
        result = Decimal(1)
        for arg in args:
            result *= Decimal(arg)
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
        return Decimal(a) + Decimal(b)

    @staticmethod
    def sub(a, b):
        return Decimal(a) - Decimal(b)

    @staticmethod
    def mul(a, b):
        return Decimal(a) * Decimal(b)

    @staticmethod
    def div(a, b):
        return Decimal(a) / Decimal(b)

    # lists and strings

    @staticmethod
    def length(items):
        return len(items)

    @staticmethod
    def select(items, ix, range_upper=None):
        if isinstance(items, (list, tuple, str)):
            ix = int(ix)
            if range_upper is not None:
                range_upper = int(range_upper)
        if range_upper is not None:
            return items[ix:range_upper]
        return items[ix]

    @staticmethod
    def contains(needle, haystack):
        return needle in haystack

    @staticmethod
    def starts_with(prefix, value):
        for ix in range(0, len(prefix)):
            if prefix[ix] != value[ix]:
                return False
        return True

    @staticmethod
    def ends_with(prefix, value):
        for ix in range(1, len(prefix) + 1):
            if prefix[-ix] != value[-ix]:
                return False
        return True

    @staticmethod
    def reverse(items):
        return reversed(items)

    @staticmethod
    def sort(*items):
        return sorted(items)

    @staticmethod
    def sort_by(key, items):
        def select(item):
            nonlocal key
            if isinstance(key, str):
                key = key.split('.')
            for k in key:
                try:
                    item = item[k]
                except KeyError:
                    return None
            return item

        return sorted(items, key=select)

    @staticmethod
    def take(n, items):
        if not isinstance(items, list):
            items = str(items)
        return items[:int(n)]

    @staticmethod
    def drop(n, items):
        if not isinstance(items, list):
            items = str(items)
        return items[int(n):]

    @staticmethod
    def take_right(n, items):
        if not isinstance(items, list):
            items = str(items)
        return items[-int(n):]

    @staticmethod
    def drop_right(n, items):
        if not isinstance(items, list):
            items = str(items)
        return items[:-int(n)]

    @staticmethod
    def head(items):
        return items[0]

    @staticmethod
    def last(items):
        return items[-1]

    @staticmethod
    def tail(items):
        return items[1:]

    @staticmethod
    def init(items):
        return items[:-1]

    @staticmethod
    def concat(*items):
        if all(isinstance(item, list) for item in items):
            result = []
            for ls in items:
                for item in ls:
                    result.append(item)
            return result
        return "".join([str(s) for s in items])

    # lists only

    @staticmethod
    def flatten(items):
        result = []
        for item in items:
            result.extend(item)
        return result

    @staticmethod
    def deepflatten(*items):
        result = []

        def helper(xss):
            if not isinstance(xss, (list, tuple)):
                result.append(xss)
                return
            for xs in xss:
                helper(xs)

        helper(items)
        return result

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

    @staticmethod
    def deepmerge(*items):
        def _merge(a, b):
            for key in b:
                if key in a:
                    if isinstance(a[key], dict) and isinstance(b[key], dict):
                        _merge(a[key], b[key])
                    else:
                        a[key] = b[key]
                else:
                    a[key] = b[key]
            return a

        return reduce(_merge, items)
