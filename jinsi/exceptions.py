class JinsiException(BaseException):
    pass


class NoParse(JinsiException):
    pass


class NoSuchEnvironmentVariable(JinsiException):
    pass


class NoSuchFunction(JinsiException):
    def __init__(self, name: str):
        self.name = name
