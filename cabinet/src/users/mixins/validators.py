from copy import copy
from typing import Any

from pydantic import root_validator, BaseModel


class CleanNoneValidatorMixin(BaseModel):

    @root_validator
    def clean_none_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        new_values: dict[str, Any] = copy(values)
        for key, value in values.items():
            if value is None:
                new_values.pop(key)
        return new_values
