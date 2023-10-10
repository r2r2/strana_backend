from src.notifications.entities import BaseNotificationCamelCaseModel


class PaymentPageResponse(BaseNotificationCamelCaseModel):
    title: str
    notify_text: str
    button_text: str
