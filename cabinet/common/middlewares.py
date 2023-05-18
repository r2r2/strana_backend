from typing import Callable, Coroutine

from config import application_config
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SafePathMiddleware(BaseHTTPMiddleware):
    """
    Deletes duplicates of root path in path
    """

    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Coroutine]
    ) -> Response:
        if path := request.scope.get("path"):
            if path.count(application_config["root_path"]) > 0:
                path: str = path.replace(application_config["root_path"], "", 1)
        request.scope["path"]: str = path
        response: Response = await call_next(request)
        return response
