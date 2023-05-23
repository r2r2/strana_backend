# pylint: disable=import-outside-toplevel
from typing import Any

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


def get_middlewares() -> list[tuple[object, dict[str, Any]]]:
    """
    middlewares
    """
    from common.handlers.middlewares import CatchExceptionsMiddleware
    from common.loggers.middlewares import LoggerMiddleware
    from common.middlewares import SafePathMiddleware
    from common.session import SessionMiddleware, SessionTimeoutMiddleware
    from config import cors_config, session_config, trusted_config

    middlewares: list[tuple[object, dict[str, Any]]] = []

    middlewares.append((CatchExceptionsMiddleware, {}))
    middlewares.append((TrustedHostMiddleware, trusted_config))
    middlewares.append((CORSMiddleware, cors_config))
    middlewares.append((SessionMiddleware, session_config))
    # middlewares.append((SessionTimeoutMiddleware, session_config))
    middlewares.append((SafePathMiddleware, {}))
    middlewares.append((LoggerMiddleware, {}))

    return middlewares
