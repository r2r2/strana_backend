import sys
from http import HTTPStatus

from starlette.requests import Request
from starlette.responses import JSONResponse
import structlog

logger = structlog.getLogger('errors')


def common_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    """
    Общий обработчик исключений
    """
    status_code = getattr(exception, "status", HTTPStatus.BAD_REQUEST)
    content = {
            "message": getattr(exception, "message", "Ошибка."),
            "reason": getattr(exception, "reason", None),
            "ok": getattr(exception, "ok", False),
        }
    logger.warning('HTTP_ERROR', status_code=status_code, content=content, exc_info=get_exc_info(exception))
    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def get_exc_info(exception: Exception) -> tuple:
    try:
        raise exception
    except Exception:
        return sys.exc_info()
