from typing import List


class Functions:
    @staticmethod
    def titlecase(value):
        return Name(value).titlecase()

    @staticmethod
    def kebabcase(value):
        return Name(value).kebabcase()

    @staticmethod
    def snakecase(value):
        return Name(value).snakecase()

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
    def concat(*strings):
        return "".join([str(s) for s in strings])

    @staticmethod
    def merge(*items):
        obj = {}
        for item in items:
            if isinstance(item, list):
                item = Functions.merge(*item)
            for key, value in item.items():
                obj[key] = value
        return obj


class Name:
    def __init__(self, name):
        parts = []
        for p1 in str(name).split("-"):
            for p2 in p1.split("_"):
                for p3 in Name.parse_camel_case(p2):
                    parts.append(p3.lower())
        self.parts = parts

    def titlecase(self):
        return "".join(part[:1].upper() + part[1:] for part in self.parts)

    def camelcase(self):
        name = self.titlecase()
        return name[:1].lower() + name[1:]

    def kebabcase(self):
        return "-".join(self.parts)

    def snakecase(self):
        return "_".join(self.parts)

    @staticmethod
    def parse_camel_case(name: str) -> List[str]:
        parts = []
        current_part = []
        last_was_upper = False
        for char in name:
            if char.isupper() and not last_was_upper:
                if current_part:
                    parts.append("".join(current_part))
                current_part = []
            elif char.islower() and last_was_upper:
                last = current_part.pop()
                if current_part:
                    parts.append("".join(current_part))
                current_part = [last]
            current_part.append(char)
            last_was_upper = char.isupper()
        if current_part:
            parts.append("".join(current_part))
        return parts
