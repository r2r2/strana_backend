from functools import wraps
from typing import Any, Tuple, Type

from common.amocrm import AmoCRM
from common.amocrm.exceptions import BaseAmocrmException
from src.booking.exceptions import BaseBookingException
from tortoise.exceptions import IntegrityError
import structlog

logger = structlog.get_logger("amocrm_sms_note")


def amocrm_sms_note(amocrm_class: Type[AmoCRM]):
    """Декоратор для отправки сообщения в сделку о реузуьтате отправки sms"""

    def initialized_func(func):

        @wraps(func)
        async def wrapper_note(self, amocrm_id, **kwargs):
            func_result, exception, text = await _get_note_message(func, self, amocrm_id=amocrm_id, **kwargs)

            if isinstance(exception, IntegrityError):
                raise exception

            async with await amocrm_class() as amocrm:
                await amocrm.send_lead_note(
                    lead_id=amocrm_id,
                    message=text
                )

            if exception:
                raise exception
            return func_result

        return wrapper_note
    return initialized_func


async def _get_note_message(func, self, amocrm_id, **kwargs) -> Tuple[Any, Any, str]:
    """Получение результата функции, ошибки при выполнении этой функции и строку для передачи в амо"""
    result = None
    exception = None
    text = "Смс с быстрой бронью не отправлено - неизвестная ошибка. "
    logger.info(f"AMOCRM sms note _get_note_message: {amocrm_id=} ")
    try:
        result = await func(self, amocrm_id, **kwargs)
    except BaseAmocrmException as amo_exception:
        exception = amo_exception
        text += amo_exception.message
    except BaseBookingException as booking_exception:
        exception = booking_exception
        text += booking_exception.message
    except Exception as e:
        exception = e
    else:
        text = "Смс с быстрой бронью успешно отправлено"
    finally:
        logger.info(f"AMOCRM sms note text: {text=} ")
        return result, exception, text.strip()
