class BaseDvizhException(Exception):
    def __init__(self, message: str, code: str = None, *args, **kwargs):
        self.code = code
        self.message: str = message


class UserPasswordWrongDvizhException(BaseDvizhException):
    ...


class TokenExpiredException(BaseDvizhException):
    ...
