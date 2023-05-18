from json import dumps, loads

from pytz import UTC
from config import auth_config
from pydantic import ValidationError
from typing import Any, Optional, Union
from datetime import datetime, timedelta
from jose.jwt import JWTError, decode, encode


def create_access_token(
    subject_type: str,
    subject: Union[str, Any],
    extra: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> dict[str, str]:
    """
    Создание токена
    """
    expire: datetime = datetime.now(tz=UTC) + timedelta(minutes=auth_config["expires"])
    if expires_delta:
        expire: datetime = datetime.now(tz=UTC) + expires_delta
    if not extra:
        extra: dict[str, Any] = dict()
    to_encode: dict[str, Union[datetime, str]] = {
        "exp": expire,
        "sub": str(subject),
        "sub_type": subject_type,
        "extra": dumps(extra),
    }
    encoded_jwt: str = encode(
        to_encode, auth_config["secret_key"], algorithm=auth_config["algorithm"]
    )
    token_type: str = auth_config["type"]
    jwt_data: dict[str, str] = dict(token=encoded_jwt, type=token_type)
    return jwt_data


def decode_access_token(
    token: str
) -> tuple[Union[int, None], Union[str, None], Union[int, None], dict[str, Any]]:
    """
    Расшифровка токена
    """
    try:
        payload = decode(token, auth_config["secret_key"], algorithms=[auth_config["algorithm"]])
        _id: Optional[int] = payload["sub"]
        _type: Optional[str] = payload["sub_type"]
        timestamp: Optional[int] = payload["exp"]
        extra: dict[str, Any] = loads(payload["extra"])
    except (JWTError, ValidationError, KeyError):
        _id = None
        _type = None
        timestamp = None
        extra = dict()
    return _id, _type, timestamp, extra


def create_email_token(subject: Union[str, Any]) -> str:
    """
    Создание токена для почты
    """
    expire: datetime = datetime.now(tz=UTC) + timedelta(minutes=10)
    to_encode: dict[str, Union[datetime, str]] = {"exp": expire, "sub": str(subject)}
    encoded_jwt: str = encode(
        to_encode, auth_config["secret_key"], algorithm=auth_config["algorithm"]
    )
    return encoded_jwt


def decode_email_token(token: str) -> Union[int, None]:
    """
    Расшифровка токена для почты
    """
    try:
        payload = decode(token, auth_config["secret_key"], algorithms=[auth_config["algorithm"]])
        _id: Optional[int] = payload["sub"]
        timestamp: int = payload["exp"]
        if datetime.now(tz=UTC) > datetime.fromtimestamp(timestamp, tz=UTC):
            _id = None
    except (JWTError, ValidationError, KeyError):
        _id = None
    return _id
