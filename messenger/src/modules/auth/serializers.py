from pydantic import BaseModel

from src.core.types import UserId
from src.entities.users import Language


class AuthTokenPayload(BaseModel):
    aud: list[str]
    exp: int
    iat: int
    iss: str
    jti: str
    user_id: UserId
    roles: list[str]
    lang: Language
