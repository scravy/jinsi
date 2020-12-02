from jinsi.util import parse_name, Dec


class Functions:

    @staticmethod
    def range_inclusive(from_, to):
        return [Dec(x) for x in range(int(from_), int(to) + 1)]

    @staticmethod
    def range_exclusive(from_, to):
        return [Dec(x) for x in range(int(from_), int(to))]

    # string functions

    @staticmethod
    def titlecase(value):
        return "".join(part[:1].upper() + part[1:] for part in parse_name(value))

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
    def take(n: int, items):
        if not isinstance(items, list):
            items = str(items)
        return items[:n]

    @staticmethod
    def drop(n: int, items):
        if not isinstance(items, list):
            items = str(items)
        return items[n:]

    @staticmethod
    def split(sep, items, maxsplit=-1):
        result = []
        if isinstance(items, list):
            current = []
            result.append(current)
            for item in items:
                if sep == item:
                    if len(result) == maxsplit:
                        return result
                    current = []
                    result.append(current)
                else:
                    current.append(item)
            return result
        items = str(items)
        return items.split(sep, maxsplit=maxsplit)

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
