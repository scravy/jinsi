class JinsiException(Exception):
    pass


class NoParseError(JinsiException):
    pass


class NoSuchVariableError(JinsiException):
    def __init__(self, name: str):
        self.name = name


class NoSuchEnvironmentVariableError(JinsiException):
    def __init__(self, name: str):
        self.name = name


class NoSuchFunctionError(JinsiException):
    def __init__(self, name: str):
        self.name = name


class NoMergePossible(JinsiException):
    pass
