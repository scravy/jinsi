class JinsiException(Exception):
    pass


class NoParseError(JinsiException):
    pass


class MalformedNameError(NoParseError):
    def __init__(self, name: str, expected: str):
        self.name = name
        self.expected = expected

    def __str__(self):
        return f"{self.name}, expected to match: {self.expected}"


class MalformedEachError(NoParseError):
    pass


class NoSuchVariableError(JinsiException):
    def __init__(self, name: str):
        self.name = name


class NoSuchEnvironmentVariableError(JinsiException):
    def __init__(self, name: str):
        self.name = name


class NoSuchFunctionError(NoParseError):
    def __init__(self, name: str):
        self.name = name


class NoMergePossible(JinsiException):
    pass


class NoCaseError(JinsiException):
    pass
