# pylint: disable=broad-except,import-outside-toplevel,lost-exception
from functools import wraps
from typing import Any, Optional, Tuple, Type

from common.amocrm import AmoCRM
from common.amocrm.exceptions import BaseAmocrmException
from src.booking.exceptions import BaseBookingException
from src.booking.use_cases.amocrm_webhook import WebhookLead
from tortoise.exceptions import IntegrityError


def amocrm_note(amocrm_class: Type[AmoCRM]):
    """Декоратор для отправки сообщения в сделку о реузуьтате отправки sms"""

    def initialized_func(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            lead_id = _get_lead_id(kwargs.get("webhook_lead"))
            func_result, exception, text = await _get_note_message(func, *args, kwargs)

            if isinstance(exception, IntegrityError):
                raise exception

            async with await amocrm_class() as amocrm:
                await amocrm.send_lead_note(
                    lead_id=lead_id,
                    message=text
                )

            if exception:
                raise exception
            return func_result

        return wrapper
    return initialized_func


def _get_lead_id(webhook_lead: Optional[WebhookLead]) -> int:
    """Получение lead_id по параметру передаваемому от вебхука"""
    if not webhook_lead:
        raise KeyError("Lead id parameter was not presented")
    return webhook_lead.lead_id


async def _get_note_message(func, *args, **kwargs) -> Tuple[Any, Any, str]:
    """Получение результата функции, ошибки при выполнении этой функции и строку для передачи в амо"""
    result = None
    exception = None
    text = "Смс с быстрой бронью не отправлено - неизвестная ошибка. "

    try:
        # note: class method execution
        kwargs.update(**args[1])
        result = await func(args[0], **kwargs)
    except BaseAmocrmException as amo_exception:
        exception = amo_exception
        text += amo_exception.message
    except BaseBookingException as booking_exception:
        exception = booking_exception
        text += booking_exception.message
    except Exception as e:
        exception = e
        import traceback
        text += traceback.format_exc().splitlines()[-1]
    else:
        text = "Смс с быстрой бронью успешно отправлено"
    finally:
        return result, exception, text
