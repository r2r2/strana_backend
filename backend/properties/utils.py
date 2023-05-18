from base64 import b64encode
from typing import Any

from app.settings import INTERNAL_LOGIN, INTERNAL_PASSWORD


def internal_access(info: Any) -> bool:
    authorization = info.context.META.get("HTTP_AUTHORIZATION")
    if not authorization:
        return False
    auth_components = authorization.split(" ")
    if not len(auth_components) == 2:
        return False
    if not auth_components[0] == "Basic":
        return False
    if not auth_components[1] == b64encode(f"{INTERNAL_LOGIN}:{INTERNAL_PASSWORD}".encode("utf-8")).decode("utf-8"):
        return False

    return True
