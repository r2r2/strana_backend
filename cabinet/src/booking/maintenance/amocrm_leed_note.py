# pylint: disable=broad-except,import-outside-toplevel,lost-exception
import re
import traceback
from functools import wraps
from typing import Any, Optional, Tuple, Type

from tortoise.exceptions import IntegrityError, TransactionManagementError

from common.amocrm import AmoCRM
from common.amocrm.exceptions import BaseAmocrmException
from src.booking.exceptions import BaseBookingException
from src.booking.use_cases.amocrm_webhook import WebhookLead


def amocrm_note(amocrm_class: Type[AmoCRM]):
    """
    Декоратор для отправки сообщения в сделку о результате отправки sms
    """

    def initialized_func(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            lead_id = kwargs.get("amocrm_id")
            func_result, exception, text = await _get_note_message(func, *args, kwargs)

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
    """
    Получение результата функции, ошибки при выполнении этой функции и строку для передачи в амо
    """
    result = None
    exception = None
    text = "Смс с быстрой бронью не отправлено - неизвестная ошибка. "

    try:
        # note: class method execution
        kwargs.update(**args[1])
        result = await func(args[0], **kwargs)
    except (BaseAmocrmException, BaseBookingException, IntegrityError, TransactionManagementError) as e:
        exception = e
        text += _format_exception_message(e)
    except Exception as e:
        exception = e
        text += _format_exception_message(e)
    else:
        text = "Смс с быстрой бронью успешно отправлено"
    finally:
        return result, exception, text


def _format_exception_message(exception) -> str:
    if isinstance(exception, (BaseAmocrmException, BaseBookingException)):
        return exception.message

    elif isinstance(exception, (IntegrityError, TransactionManagementError)):
        traceback_str = traceback.format_exc()

        constraint_match = re.search(r'constraint "(.*?)"', traceback_str)
        if constraint_match:
            constraint_name = constraint_match.group(1)

            if constraint_name == "users_user_unique_together_email_type":
                return "Найден пользователь с такой же почтой."

    return traceback.format_exc().splitlines()[-1]
