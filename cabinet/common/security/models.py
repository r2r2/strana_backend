from hmac import compare_digest
from typing import Any

from pydantic import BaseModel, root_validator


class BasePasswordModel(BaseModel):
    password_1: Any
    password_2: Any

    @property
    def password(self):
        return self.password_1


class PasswordModel(BasePasswordModel):
    password_1: str
    password_2: str

    @root_validator
    def validate_password(cls, values: dict[str, Any]) -> dict[str, Any]:
        password_1: str = values.get("password_1")
        password_2: str = values.get("password_2")
        if not compare_digest(password_1, password_2):
            raise ValueError("passwords_not_match")
        if len(password_1) < 7:
            raise ValueError("passwords_too_short")
        values["password"]: str = password_1
        return values
