from ..entities import BaseNotificationModel


class OnboardingModel(BaseNotificationModel):
    id: int
    message: str
    slug: str
    button_text: str
