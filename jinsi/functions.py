from jinsi.util import parse_name, Dec


class Functions:
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

    @staticmethod
    def object(key, value):
        return {key: value}

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

    @staticmethod
    def concat(*items):
        if all(isinstance(item, list) for item in items):
            result = []
            for ls in items:
                for item in ls:
                    result.append(item)
        return "".join([str(s) for s in items])

    @staticmethod
    def merge(*items):
        obj = {}
        for item in items:
            if isinstance(item, list):
                item = Functions.merge(*item)
            for key, value in item.items():
                obj[key] = value
        return obj
