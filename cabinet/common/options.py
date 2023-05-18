from typing import Any


class InitOption(object):
    """
    Class for hardcoded init filters
    """

    def __init__(self, field: str, value: Any) -> None:
        self.field: str = field
        self.value: Any = value

    def as_filter(self) -> dict[str, Any]:
        return {self.field: self.value}


class RequestOption(object):
    """
    Class for init filter using request_data
    """

    def __init__(self, field: str, dependency: str) -> None:
        self.field: str = field
        self.dependency: str = dependency
        self.choices: list["RequestOption"] = list()

    def as_filter(self, value: Any) -> dict[str, Any]:
        return {self.field: value}

    def __str__(self) -> str:
        return self.dependency

    def __or__(self, other: "RequestOption"):
        self.choices.append(other)
        return self
