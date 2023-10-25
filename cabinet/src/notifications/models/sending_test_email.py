from ..entities import BaseNotificationModel


class SendingTestEmailModel(BaseNotificationModel):
    """
    Модель запроса тестового апи для отправки писем (отладка шаблонов).
    """

    recipients: list[str]
    slug: str
    context: dict

