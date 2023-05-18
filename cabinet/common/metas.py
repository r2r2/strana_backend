from copy import copy
from typing import Union, Any


class ChoiceMeta(type):
    """
    Allows class to be a choice constant
    """

    def __new__(mcs, name: str, bases: Any, attrs: dict[str, Any]) -> type:
        new_attrs: dict[str, Any] = copy(attrs)
        int_choices: list[int] = list()
        str_choices: list[str] = list()
        for field, value in attrs.items():
            if isinstance(value, tuple) and len(value) == 2 and field.upper() == field:
                new_attrs[field]: Union[int, str] = value[0]
                if isinstance(value[0], str):
                    str_choices.append(value[0])
                elif isinstance(value[0], int):
                    int_choices.append(value[0])
                new_attrs[f"{field}_LABEL"]: str = value[1]
        if int_choices and str_choices:
            raise ValueError("All the choices must be one type instances")
        new_attrs["choices"]: tuple = tuple(int_choices) if int_choices else tuple(str_choices)
        return super().__new__(mcs, name, bases, new_attrs)
